import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from typing import List, Dict, Any, Optional
import logging

# Set up logging
logger = logging.getLogger(__name__)

def weighted_reciprocal_rank(doc_lists, weights=None):
    """
    This is a modified version of the function in the langchain repo
    https://github.com/langchain-ai/langchain/blob/master/libs/langchain/langchain/retrievers/ensemble.py

    Perform weighted Reciprocal Rank Fusion on multiple rank lists.
    You can find more details about RRF here:
    https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf

    Args:
        doc_lists: A list of rank lists, where each rank list contains unique items.
        weights: A list of weights for the documents

    Returns:
        list: The final aggregated list of items sorted by their weighted RRF
                scores in descending order.
    """
    c = 60  # c comes from the paper
    if not weights:
        weights = [1, 0.2]

    if len(doc_lists) != len(weights):
        raise ValueError(
            "Number of rank lists must be equal to the number of weights."
        )

    # Create a union of all unique documents in the input doc_lists
    all_documents = set()
    for doc_list in doc_lists:
        for doc in doc_list:
            all_documents.add(doc["text"])

    # Initialize the RRF score dictionary for each document
    rrf_score_dic = {doc: 0.0 for doc in all_documents}

    # Calculate RRF scores for each document
    for doc_list, weight in zip(doc_lists, weights):
        for rank, doc in enumerate(doc_list, start=1):
            rrf_score = weight * (1 / (rank + c))
            rrf_score_dic[doc["text"]] += rrf_score

    # Sort documents by their RRF scores in descending order
    sorted_documents = sorted(
        rrf_score_dic.keys(), key=lambda x: rrf_score_dic[x], reverse=True
    )

    # Map the sorted page_content back to the original document objects
    page_content_to_doc_map = {
        doc["text"]: doc for doc_list in doc_lists for doc in doc_list
    }
    sorted_docs = [
        page_content_to_doc_map[page_content] for page_content in sorted_documents
    ]

    return sorted_docs


class BGEReranker:
    """
    BGE-Reranker-v2 for document reranking using Hugging Face transformers.
    """
    
    def __init__(self, model_name: str = "BAAI/bge-reranker-v2-m3", device: str = "auto"):
        """
        Initialize the BGE Reranker.
        
        Args:
            model_name: Hugging Face model name for BGE reranker
            device: Device to run the model on ('auto', 'cpu', 'cuda')
        """
        self.model_name = model_name
        self.device = device
        self.tokenizer = None
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the BGE reranker model and tokenizer."""
        try:
            logger.info(f"Loading BGE reranker model: {self.model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
            
            # Set device
            if self.device == "auto":
                self.device = "cuda" if torch.cuda.is_available() else "cpu"
            
            self.model.to(self.device)
            self.model.eval()
            logger.info(f"BGE reranker loaded successfully on {self.device}")
            
        except Exception as e:
            logger.error(f"Failed to load BGE reranker: {e}")
            raise
    
    def rerank_documents(self, query: str, documents: List[Dict[str, Any]], top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Rerank documents based on their relevance to the query using BGE reranker.
        
        Args:
            query: The search query
            documents: List of documents to rerank (each should have 'text' field)
            top_k: Number of top documents to return (None for all)
            
        Returns:
            List of reranked documents sorted by relevance score
        """
        if not documents:
            return []
        
        try:
            # Prepare query-document pairs
            pairs = []
            for doc in documents:
                text = doc.get('text', '')
                if text.strip():  # Only include non-empty documents
                    pairs.append([query, text])
            
            if not pairs:
                return []
            
            # Tokenize and get scores
            with torch.no_grad():
                inputs = self.tokenizer(
                    pairs,
                    padding=True,
                    truncation=True,
                    return_tensors='pt',
                    max_length=512
                ).to(self.device)
                
                scores = self.model(**inputs, return_dict=True).logits.view(-1, ).float()
                scores = torch.sigmoid(scores)  # Convert to probabilities
            
            # Create documents with scores
            scored_docs = []
            score_idx = 0
            
            for doc in documents:
                text = doc.get('text', '')
                if text.strip():
                    # Create a copy of the document with the rerank score
                    scored_doc = doc.copy()
                    scored_doc['rerank_score'] = scores[score_idx].item()
                    scored_docs.append(scored_doc)
                    score_idx += 1
            
            # Sort by rerank score (descending)
            scored_docs.sort(key=lambda x: x['rerank_score'], reverse=True)
            
            # Return top_k if specified
            if top_k is not None:
                return scored_docs[:top_k]
            
            return scored_docs
            
        except Exception as e:
            logger.error(f"Error in BGE reranking: {e}")
            # Fallback: return original documents
            return documents


def bge_rerank_documents(query: str, doc_lists: List[List[Dict[str, Any]]], 
                        top_k: Optional[int] = None, 
                        model_name: str = "BAAI/bge-reranker-v2-m3") -> List[Dict[str, Any]]:
    """
    Rerank documents from multiple retrieval methods using BGE reranker.
    
    Args:
        query: The search query
        doc_lists: List of document lists from different retrieval methods
        top_k: Number of top documents to return
        model_name: BGE reranker model name
        
    Returns:
        List of reranked documents sorted by relevance
    """
    try:
        # Initialize reranker
        reranker = BGEReranker(model_name=model_name)
        
        # Combine all documents from different retrieval methods
        all_documents = []
        seen_texts = set()
        
        for doc_list in doc_lists:
            for doc in doc_list:
                text = doc.get('text', '')
                if text and text not in seen_texts:
                    all_documents.append(doc)
                    seen_texts.add(text)
        
        if not all_documents:
            logger.warning("No documents to rerank")
            return []
        
        logger.info(f"Reranking {len(all_documents)} unique documents with BGE reranker")
        
        # Rerank documents
        reranked_docs = reranker.rerank_documents(query, all_documents, top_k)
        
        logger.info(f"BGE reranking completed, returned {len(reranked_docs)} documents")
        return reranked_docs
        
    except Exception as e:
        logger.error(f"BGE reranking failed: {e}")
        # Fallback to weighted reciprocal rank
        logger.info("Falling back to weighted reciprocal rank")
        return weighted_reciprocal_rank(doc_lists)
