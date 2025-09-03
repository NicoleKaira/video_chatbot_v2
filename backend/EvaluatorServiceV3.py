import asyncio
import json
import os
import time
from typing import List


from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_openai.embeddings import AzureOpenAIEmbeddings

from ragas import SingleTurnSample
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    FactualCorrectness, LLMContextPrecisionWithReference, ResponseRelevancy, Faithfulness, LLMContextRecall
)

from chatservice.chatservice import ChatService
from brokerservice.brokerService import BrokerRepository

load_dotenv()
class EvaluatorService:
    def __init__(self, chat_service: ChatService, broker_service: BrokerRepository, questions=None, ground_truths=None):
        self.chat_service = chat_service
        self.broker_service = broker_service
        
        self.llm_evaluator = AzureChatOpenAI(
            azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
            api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
            api_version=os.environ.get("OPENAI_API_VERSION"),
            azure_deployment=os.environ.get("YOUR_DEPLOYMENT_NAME"),
            temperature=0
        )

        self.metrics = [
            faithfulness,
            answer_relevancy,
            FactualCorrectness(),
        ]


# Testing for Generic Questions
        self.generic_questions = [
            "What is the title of this course?",
            "Who is the lecturer of this course?",
            "When is the first lab test?",
            "What is the test format for Lab Test 2 and Quiz?",
            "What is the difference between the first half to the second half of the course?",
            "What is the course schedule for this course?",
            "Who is the professor incharge of Assignment 1 to 3?",
            "Are the Lab session Compulsory to attend?",
            "What is the purpose of tutorials?",
            "What courses is SC1007 a pre-requisite to?",
            "Who will be teaching the first and second half of this course?",
            "What are the assessment components?",
            "What are the Algorithm Design Strategies presented in the lecture?",
            "What will be covered in the next lecture?",
            "What are some of the questions the students asked at the end of the lecture?",
            "How can I do well in this course?"
        ]
        self.generic_answer = [
            "The course title is SC1007 Data Structure and Algorithm.",
            "The lecturer in this lecture is Dr. Loke.",
            "The first lab test is scheduled for Recess Week on 2 March 2023.",
            "Lab Test 2 and the quiz, held together on 20 April, will include multiple-choice questions covering concepts from Week 1 to Week 13 such as linked lists, binary trees, hash tables, graphs, dynamic programming, and matching problems and three programming questions in a two-hour test, with the programming format similar to Lab Test 1.",
            "The first half covers linked lists, stacks and queues, and binary trees, while the second half covers hash tables, graph problems, search algorithms, backtracking, permutations, dynamic programming, and matching problems.",
            "The course schedule covers topics in sequence: Introduction to Data Structure; Linked List (LL) and Linear Search; Stack and Queue (SQ), Arithmetic Operations; Binary Trees (BT) and Binary Search Trees (BST); Analysis of Algorithm (AA); Hash Table; Basic Graph (G); DFS with Backtracking/Permutation; Dynamic Programming (DP); and Revision and quizzes, with corresponding labs and assignments for each topic.",
            "Dr. Owen is in charge of Assignments 1 to 3, which together account for 20% of the course grade.",
            "The lab sessions are not graded and attendance is not compulsory, but attendance is taken, and missing them may negatively affect performance in lab tests.",
            "The purpose of the tutorials is to focus on concepts rather than programming, complementing the lectures by reinforcing theoretical understanding without providing code.",
            "The course SC1007 is a prerequisite for SC2001.",
            "The first half will be taught by Dr. Owen while the second half is by Dr. Loke.",
            "The assessment components are assignments, two lab tests, and a final quiz, covering concepts from both Part 1 and Part 2 of the course. Attendance for tests is compulsory.",
            "The algorithm design strategies presented include brute force, divide and conquer, greedy, decrease and conquer, transform and conquer, and iterative improvement.",
            "The next lecture will cover analysis of algorithms, including time complexity, space complexity, best, worst, and average cases, order of growth, and Big O notation.",
            "A student asked whether it is possible to solve recursive relations so that the time complexity becomes constant.",
            "The lecturer advised practicing labs and assignments and focusing on implementing algorithms yourself instead of relying on provided solutions."
        ]



# Testing for multivideos questions
        # self.question_for_multivideos = [
        #     "According to the lecturer, is the lab graded, and how is attendance handled?",
        #     "What penalty does the lecturer state for plagiarism in assignments?",
        #     "What programming language does the module use throughout, including the second half?",
        #     "List the three essential characteristics of an algorithm mentioned by the lecturer.",
        #     "When is the combined lab test and quiz scheduled, and what does the quiz cover?",
        #     "In the factorial example with a while loop, how does computational time scale with N?",
        #     "For a nested loop that sums all elements in an NxN matrix, what is the time complexity?",
        #     "What cases should be considered when analyzing selection structures (if/else) for time complexity mentioned in this lecture?",
        #     "What is the recurrence for counting comparisons in a simple recursive array scan, and what does it solve to?",
        #     "In a binary-tree traversal that makes two recursive calls per node, how does the number of operations grow with the number of levels K?",
        #     "Across the two lectures, which topics are planned after the analysis of algorithms and when might hash tables be covered?",
        #     "Which lecture previews asymptotic notation and which one defines Big O, Big Ω, and Big Θ in detail?",
        #     "Summarize how recursion impacts time and space across the two lectures using examples given.",
        #     "From both lectures, what is the difference between an algorithm and a program, and how is efficiency evaluated?",
        #     "Combine the examples: which method is most efficient for summing 1..N, and how is this justified by the complexity principles?"
        # ]

        # self.answer_for_multivideos = [
        #     "The lab itself is not graded, but attendance is still taken. Skipping labs may hurt performance in lab tests. (Reference: Sc1007_videolecture)",
        #     "Assignments are checked for plagiarism; getting caught results in zero marks for that assignment. (Reference: Sc1007_videolecture)",
        #     "C programming. (Reference: Sc1007_videolecture)",
        #     "Correctness, precision (unambiguous steps), and finiteness (must terminate in finite time). (Reference: Sc1007_videolecture)",
        #     "Week 14 (April 20): a combined two-hour lab test and quiz. The MCQ tests concepts from Weeks 1-13, including analysis of algorithms. (Reference: Sc1007_videolecture)",
        #     "It scales linearly with N; time complexity is linear (O(N)). (Reference: Lecture2_Sc1007)",
        #     "Quadratic time, O(N^2); more generally MxN operations for an MxN matrix. (Reference: Lecture2_Sc1007)",
        #     "Best case, worst case, and average case (with probabilities). (Reference: Lecture2_Sc1007)",
        #     "W(N) = 1 + W(N-1) with base W(1)=1; it solves to linear growth, i.e., N total comparisons. (Reference: Lecture2_Sc1007)",
        #     "It follows a geometric series (1 + 2 + 4 + … + 2^(K-1)), i.e., exponential growth in K. (Reference: Lecture2_Sc1007)",
        #     "Both lectures mention moving on to hash tables and graph problems. Lecture2_Sc1007 notes hash tables will be covered on Monday (or Wednesday) depending on time. (Reference: Sc1007_videolecture + Lecture2_Sc1007)",
        #     "Sc1007_videolecture previews that asymptotic notation (e.g., Big O) will be covered; Lecture2_Sc1007 defines Big O, Big Ω (Omega), and Big Θ (Theta) and explains ignoring constants and focusing on growth order. (Reference: Sc1007_videolecture + Lecture2_Sc1007)",
        #     "Sc1007_videolecture uses Fibonacci to show naive recursion can be exponential in time; Lecture2_Sc1007 shows factorial recursion is linear time but uses extra stack memory compared to iteration. (Reference: Sc1007_videolecture + Lecture2_Sc1007)",
        #     "Sc1007_videolecture explains an algorithm is a well-defined procedure while a program is its implementation; Lecture2_Sc1007 explains efficiency is evaluated via time/space complexity and asymptotic growth, not raw runtime constants. (Reference: Sc1007_videolecture + Lecture2_Sc1007)",
        #     "Using the arithmetic series formula N/2*(1+N) is most efficient (constant-time operations), justified by Lecture2_Sc1007's principle of focusing on lowest order of growth and ignoring constants. (Reference: Sc1007_videolecture + Lecture2_Sc1007)"
        # ]
#####################part2
        # self.question_for_multivideos = [
        #     "What searching approaches are mentioned and how do their time complexities differ?",
        #     "Considering the course logistics from both lectures, what assessments contribute to the final grade?",
        #     "Using both lectures, explain why constants are ignored in asymptotic analysis and give an example where N^2 + 100 and N^2 are treated the same.",
        #     "Across the lectures, which graph-related topics are planned and what real-world path problem is used as an example?",
        #     "What guidance is given about coding vs. concepts across the lectures, and how should students prepare?",
        #     "What is the purpose of analyzing algorithms before implementation?",
        #     "Define time complexity vs. space complexity in the context of the lectures.",
        #     "Why is counting primitive operations preferred over raw wall-clock time for complexity analysis?",
        #     "Name the three asymptotic notations discussed and what they broadly signify.",
        #     "Give an example where a logarithmic-time algorithm is preferable to a linear-time algorithm and explain why.",
        #     "Why might an algorithm with lower time complexity be rejected in practice?",
        #     "What is meant by 'order of growth' and why are constants and lower-order terms often ignored?",
        #     "Provide an example of a geometric series arising in recursive analysis.",
        #     "What core problem types are highlighted in the module and why are they important?",
        #     "State one reason why naive recursive Fibonacci is inefficient compared to an iterative approach."
        # ]

        # self.answer_for_multivideos = [
        #     "Linear search (Sc1007_videolecture) is O(N); hash-based lookup (Lectures 1 & 2 plan) targets O(1) average time with extra space. (Reference: Sc1007_videolecture + Lecture2_Sc1007)",
        #     "Assignments (two parts totaling 40%), two lab tests (20% each), and a final quiz (20%), as outlined in Sc1007_videolecture; Lecture2_Sc1007 reiterates upcoming topics tied to assessments release (e.g., after hash tables). (Reference: Sc1007_videolecture (+ context from Lecture2_Sc1007))",
        #     "Lecture2_Sc1007 explicitly shows that as N grows large, additive constants (like +100) and constant factors have negligible impact on growth, so N^2 + 100 and N^2 are both Θ(N^2). (Reference: Lecture2_Sc1007 (previewed in Sc1007_videolecture))",
        #     "Planned topics include BFS, DFS, backtracking, permutations, dynamic programming, and matching; Google Maps shortest path is given as a real-world example (Sc1007_videolecture). (Reference: Sc1007_videolecture (+ plans mentioned across both))",
        #     "Lectures focus on concepts; implementation practice is expected in labs/assignments. Students should practice coding themselves rather than relying on solutions. (Reference: Sc1007_videolecture (reinforced by Lecture2_Sc1007's focus on analysis))",
        #     "To compare potential solutions by their efficiency and scalability (time and space) with respect to input size before coding. (Reference: Either)",
        #     "Time complexity measures how the number of operations grows with input size; space complexity measures memory/storage usage growth with input size. (Reference: Either)",
        #     "Wall-clock time depends on hardware, whereas counting primitive operations abstracts away machine differences and focuses on algorithmic growth. (Reference: Either)",
        #     "Big O (upper bound), Big Ω (lower bound), Big Θ (tight bound/same growth rate). (Reference: Either (defined in Lecture2_Sc1007))",
        #     "Binary search or balanced-tree operations take O(log N), requiring far fewer steps than O(N) as N grows, thus much faster for large inputs. (Reference: Either (implied by both; detailed in Lecture2_Sc1007))",
        #     "It might require too much memory (space complexity) or not fit device constraints, necessitating a time-space trade-off. (Reference: Either)",
        #     "Order of growth describes how runtime/memory scales with problem size; constants/lower-order terms are negligible for large N. (Reference: Either (emphasized in Lecture2_Sc1007))",
        #     "A binary-tree traversal with two recursive calls per node yields 1 + 2 + 4 + … + 2^(K-1). (Reference: Either (seen in Lecture2_Sc1007))",
        #     "Searching, graph problems, sorting, string processing, combinatorial, computational geometry, and optimization—core to many CS applications. (Reference: Either (catalogued in Sc1007_videolecture))",
        #     "Naive recursion recomputes overlapping subproblems, leading to exponential time, whereas iteration uses linear time. (Reference: Either (example in Sc1007_videolecture, principles echoed in Lecture2_Sc1007))"
        # ]

################################part3
        self.question_for_multivideos = [
            "What is the exact date and time of the first lab test?",
            "Which platform will be used to submit assignments (e.g., NTULearn/Canvas) and how are files to be named?",
            "What are the room numbers/venues for the physical tutorial sessions and labs?",
            "What is the detailed grading rubric for the final quiz (marks allocation for each section)?",
            "Are late submissions allowed for assignments and what are the exact penalties or grace periods?",
            "Which C standard and compiler flags are required for lab tests (e.g., C11, -Wall, -O2)?",
            "What are the official collaboration rules (e.g., pair work allowed, discussion limits) for assignments?",
            "What are the lecturer's and TAs' weekly office hours and locations?",
            "Provide the complete timetable (exact dates & times) for lectures, tutorials, and labs for Weeks 8 to 14.",
            "What is the make-up policy for missed lab tests due to medical reasons (documentation required, reschedule window)?"
        ]

        self.answer_for_multivideos = [
            "I am unsure of the answer.",
            "I am unsure of the answer.",
            "I am unsure of the answer.",
            "I am unsure of the answer.",
            "I am unsure of the answer.",
            "I am unsure of the answer.",
            "I am unsure of the answer.",
            "I am unsure of the answer.",
            "I am unsure of the answer.",
            "I am unsure of the answer."
        ]

################################################################################################
    ##### PART1 #####   temporal
        # self.time_sensitive_questions = [
        #     "What is mentioned at 33 minutes of the lecture?",
        #     "What was discussed in 27:00 of the lecture?",
        #     "When was the difference between algorithm and program discussed?",
        #     "What concept is explained around 45:00 into the lecture?",
        #     "At what point in the lecture does it start discussing How do we solve the different searching, graph and combinatorial problems?",
        #     "What does the lecturer say right after the algorithm Vs program at 23 minutes in the video?",
        #     "Does the lecturer explain graph problems before or after Combinatorial problems?",
        #     "What was discussed before Learning outcomes?",
        #     "What topic is discussed right after Algorithm Design Strategies?",
        #     "Which topic comes just before the explanation of the Sorting Problem?"
        # ]

        # self.time_sensitive_answers = [
        #     "At the 33-minute mark, the lecturer mentioned that the module will mainly cover problem types such as searching, graph problems, and combinatorial problems involving permutations.",
        #     "The lecturer discussed the Fibonacci sequence, using it as an example to illustrate algorithmic thinking and recursive problem-solving.",
        #     "The difference between an algorithm and a program was discussed around 21:00.",
        #     "Around the 45-minute mark, the lecturer explains stable sorting algorithms, highlighting that they preserve the relative order of repeated elements during sorting, using student marks across modules as an example.",
        #     "It begins discussing how to solve different searching, graph, and combinatorial problems around the 53-minute mark, introducing data structures and algorithmic strategies like brute force, divide and conquer, greedy, and more.",
        #     "Right after explaining the difference between an algorithm and a program around the 23-minute mark, the lecturer introduces a simple example of summing numbers from 1 to N using different algorithmic approaches, such as a for loop, a mathematical formula, and recursion.",
        #     "The lecturer explains graph problems before combinatorial problems.",
        #     "Before discussing the learning outcomes, the lecturer went through the course schedule.",
        #     "Right after algorithm design strategies, the lecturer summarizes the overview of the lecture and discusses what will be taught in the next few weeks in this module.",
        #     "The combinatorial problem is discussed just before the explanation of the sorting problem."
        # ]
     ##### PART2 #####
    #     self.time_sensitive_questions = [
    #     "Which week or lecture covers the topic Hash Tables?",
    #     "During which part of the lecture (start/middle/end) is Computer Science Programme Structure discussed?",
    #     "What is covered in the last 5 minutes of the lecture?",
    #     "What was discussed at the start of the lecture?",
    #     "What was discussed at the end of the lecture?",
    #     "What was said 2 minutes before Problem Type was introduced?",
    #     "When did the lecturer mention the learning outcomes of this course?",
    #     "What topic is discussed between 23:00 and 26:00?",
    #     "When did the lecturer mention the overview of the lecture?",
    #     "What topics were discussed between the 2 to 8 minutes of the lecture?"
    # ]

    #     self.time_sensitive_answers = [
    #     "The topic of Hash Tables is covered in Week 8 of the lecture.",
    #     "The Computer Science Programme Structure is discussed at the beginning of the lecture.",
    #     "In the last 5 minutes of the lecture, the lecturer emphasizes the importance of practicing coding independently rather than relying on provided solutions, highlighting that true understanding comes from implementing algorithms yourself. He also concludes the lecture and ends the live stream.",
    #     "At the start of the lecture, Dr. Loke gave an introduction to the module, explained the format of the live stream and lecture notes, and outlined the topics to be covered, including the analysis of algorithms, hash tables, and graph problems in the second half of the module.",
    #     "A Question-and-answer session with the students, where the lecturer discussed how labs and tutorials could support their learning in the module.",
    #     "Two minutes before the Problem Type was introduced, the Fibonacci Sequence was discussed.",
    #     "The lecturer mentioned the learning outcomes of the course between 07:00 and 09:45",
    #     "Between 23:00 and 26:00, an example on the arithmetic series is discussed.",
    #     "The lecturer mentioned the overview of the lecture 57:00 onwards.",
    #     "The lecturer discussed the course schedule and the learning outcomes of the course."
    # ]
################################################################################################

    async def get_dataset(self, video_id):
        results = []  # This will store the results for all questions

        # Iterate through the questions and evaluate the answers
        for i in range(len(self.questions)):
            retrieval_results, context = self.chat_service.retrieve_results_prompt_clean(video_id, self.questions[i])
            print(str(i) + " get_dataset " + str(context))
            answer = self.chat_service.generate_video_prompt_response(retrieval_results, self.questions[i])

            # Evaluate metrics
            context_precision = await self.evaluate_context_precision(self.questions[i], self.ground_truths[i], context)
            response_relevancy = await self.evaluate_response_relevancy(self.questions[i], answer, context)
            faithfulness_result = await self.evaluate_faithfulness(self.questions[i], answer, context)
            context_recall = await self.evaluate_context_recall(self.questions[i], answer, self.ground_truths[i],
                                                                context)

            # Store the results for this question in a dictionary
            result = {
                'question': self.questions[i],
                'ground_truth': self.ground_truths[i],
                'context': context,
                'answer': answer,
                'context_precision': context_precision,
                'response_relevancy': response_relevancy,
                'faithfulness_result': faithfulness_result,
                'context_recall': context_recall
            }

            results.append(result)

        with open("evaluation_results.json", mode='w', newline='') as jsonfile:
            json.dump(results, jsonfile, indent=4)

#nicole multivideo RAGV4.0
    async def get_dataset_mutlivid(self, video_ids):
        results = []  # This will store the results for all questions

        # Iterate through the questions and evaluate the answers
        for i in range(len(self.question_for_multivideos)):
            start_time =time.time()

            retrieval_results, context = self.chat_service.retrieve_results_prompt_clean_multivid(video_ids, self.question_for_multivideos[i])
            print(str(i) + " get_dataset " + str(context))
            answer = self.chat_service.generate_video_prompt_response(retrieval_results, self.question_for_multivideos[i])

            # Evaluate metrics
            context_precision = await self.evaluate_context_precision(self.question_for_multivideos[i], self.answer_for_multivideos[i], context)
            response_relevancy = await self.evaluate_response_relevancy(self.question_for_multivideos[i], answer, context)
            faithfulness_result = await self.evaluate_faithfulness(self.question_for_multivideos[i], answer, context)
            context_recall = await self.evaluate_context_recall(self.question_for_multivideos[i], answer, self.answer_for_multivideos[i],
                                                                context)

            end_time = time.time()
            time_taken = end_time-start_time
            # Store the results for this question in a dictionary
            result = {
                'question': self.question_for_multivideos[i],
                'ground_truth': self.answer_for_multivideos[i],
                'context': context,
                'answer': answer,
                'context_precision': context_precision,
                'response_relevancy': response_relevancy,
                'faithfulness_result': faithfulness_result,
                'context_recall': context_recall,
                'time_taken': time_taken
            }

            results.append(result)

        with open("MultivideoV4.0_evaluation_results4.json", mode='w', newline='') as jsonfile:
            json.dump(results, jsonfile, indent=4)
        
        return


    async def get_dataset_pre(self, video_id):
        results = []  # This will store the results for all questions

        # Iterate through the questions and evaluate the answers
        for i in range(len(self.questions)):
            retrieval_results, context = self.chat_service.retrieve_results_prompt(video_id, self.questions[i])
            print(str(i) + " get_dataset_pre " + str(context))
            answer = self.chat_service.generate_video_prompt_response(retrieval_results, self.questions[i])

            # Evaluate metrics
            context_precision = await self.evaluate_context_precision(self.questions[i], self.ground_truths[i], context)
            response_relevancy = await self.evaluate_response_relevancy(self.questions[i], answer, context)
            faithfulness_result = await self.evaluate_faithfulness(self.questions[i], answer, context)
            context_recall = await self.evaluate_context_recall(self.questions[i], answer, self.ground_truths[i],
                                                                context)

            # Store the results for this question in a dictionary
            result = {
                'question': self.questions[i],
                'ground_truth': self.ground_truths[i],
                'context': context,
                'answer': answer,
                'context_precision': context_precision,
                'response_relevancy': response_relevancy,
                'faithfulness_result': faithfulness_result,
                'context_recall': context_recall
            }

            results.append(result)

        with open("evaluation_results_pre.json", mode='w', newline='') as jsonfile:
            json.dump(results, jsonfile, indent=4)

    async def get_dataset_naive(self, video_id):
        results = []  # This will store the results for all questions

        # Iterate through the questions and evaluate the answers
        for i in range(len(self.questions)):
            retrieval_results, context = self.chat_service.retrieve_results_prompt_naive(video_id, self.questions[i])
            print(str(i) + " get_dataset_naive " + str(context))
            answer = self.chat_service.generate_video_prompt_response(retrieval_results, self.questions[i])

            # Evaluate metrics
            context_precision = await self.evaluate_context_precision(self.questions[i], self.ground_truths[i], context)
            response_relevancy = await self.evaluate_response_relevancy(self.questions[i], answer, context)
            faithfulness_result = await self.evaluate_faithfulness(self.questions[i], answer, context)
            context_recall = await self.evaluate_context_recall(self.questions[i], answer, self.ground_truths[i],
                                                                context)

            # Store the results for this question in a dictionary
            result = {
                'question': self.questions[i],
                'ground_truth': self.ground_truths[i],
                'context': context,
                'answer': answer,
                'context_precision': context_precision,
                'response_relevancy': response_relevancy,
                'faithfulness_result': faithfulness_result,
                'context_recall': context_recall
            }

            results.append(result)

        with open("evaluation_results_naive.json", mode='w', newline='') as jsonfile:
            json.dump(results, jsonfile, indent=4)

    async def get_dataset_clean_naive(self, video_id):
        results = []  # This will store the results for all questions

        # Iterate through the questions and evaluate the answers
        for i in range(len(self.questions)):
            retrieval_results, context = self.chat_service.retrieve_results_prompt_clean_naive(video_id, self.questions[i])
            print(str(i) + " get_dataset_naive " + str(context))
            answer = self.chat_service.generate_video_prompt_response(retrieval_results, self.questions[i])

            # Evaluate metrics
            context_precision = await self.evaluate_context_precision(self.questions[i], self.ground_truths[i], context)
            response_relevancy = await self.evaluate_response_relevancy(self.questions[i], answer, context)
            faithfulness_result = await self.evaluate_faithfulness(self.questions[i], answer, context)
            context_recall = await self.evaluate_context_recall(self.questions[i], answer, self.ground_truths[i],
                                                                context)

            # Store the results for this question in a dictionary
            result = {
                'question': self.questions[i],
                'ground_truth': self.ground_truths[i],
                'context': context,
                'answer': answer,
                'context_precision': context_precision,
                'response_relevancy': response_relevancy,
                'faithfulness_result': faithfulness_result,
                'context_recall': context_recall
            }

            results.append(result)

        with open("evaluation_results_naive_clean.json", mode='w', newline='') as jsonfile:
            json.dump(results, jsonfile, indent=4)

    async def get_dataset_t(self, video_id):
        results = []  # This will store the results for all questions

        # Iterate through the questions and evaluate the answers
        for i in range(len(self.time_sensitive_questions)):
            start_time = time.time()
            retrieval_results, context = self.chat_service.retrieve_results_prompt_clean(video_id, self.time_sensitive_questions[i])
            print(str(i) + " get_dataset " + str(context))
            answer = self.chat_service.generate_video_prompt_response(retrieval_results, self.time_sensitive_questions[i])

            # Evaluate metrics
            context_precision = await self.evaluate_context_precision(self.time_sensitive_questions[i], self.time_sensitive_answers[i], context)
            response_relevancy = await self.evaluate_response_relevancy(self.time_sensitive_questions[i], answer, context)
            faithfulness_result = await self.evaluate_faithfulness(self.time_sensitive_questions[i], answer, context)
            context_recall = await self.evaluate_context_recall(self.time_sensitive_questions[i], answer, self.time_sensitive_answers[i],
                                                                context)

            end_time = time.time()
            time_taken = end_time - start_time

            # Store the results for this question in a dictionary
            result = {
                'question': self.time_sensitive_questions[i],
                'ground_truth': self.time_sensitive_answers[i],
                'context': context,
                'answer': answer,
                'context_precision': context_precision,
                'response_relevancy': response_relevancy,
                'faithfulness_result': faithfulness_result,
                'context_recall': context_recall,
                'time_taken': time_taken
            }

            results.append(result)
            print("Iteration " + str(i) + " took " + str(time_taken) + " seconds")

        with open("evaluation_results_t.json", mode='w', newline='') as jsonfile:
            json.dump(results, jsonfile, indent=4)

    #nicoles below
    async def get_dataset_t_with_llm(self, video_id):
        results = []  # This will store the results for all questions

        # questions_template = self.time_sensitive_questions
        # answers_template = self.time_sensitive_answers
        questions_template = self.generic_questions
        answers_template = self.generic_answer


        for i in range(len(questions_template)):
           
            start_time = time.time()
            
            question = questions_template[i]
            # Step 1: Check if the question is temporal
            is_temporal_res = await self.chat_service.is_temporal_question(question)
            is_temporal = is_temporal_res.is_temporal
            timestamp = is_temporal_res.timestamp

            context = []
            answer = ""

            if is_temporal:
                if timestamp:
                    # Step 3: Retrieve chunks based on the timestamp
                    retrieval_results, context = self.chat_service.retrieve_chunks_by_timestamp(video_id, timestamp)
                    answer = self.chat_service.generate_video_prompt_response(retrieval_results, question)
                else:
                    # fallback if timestamp not extractable
                    retrieval_results, context = self.chat_service.retrieve_results_prompt_clean(video_id, question)
                    answer = self.chat_service.generate_video_prompt_response(retrieval_results, question)
            else:
                retrieval_results, context = self.chat_service.retrieve_results_prompt_clean(video_id, question)
                answer = self.chat_service.generate_video_prompt_response(retrieval_results, question)
            

            
            # Evaluate metrics
            context_precision = await self.evaluate_context_precision(questions_template[i], answers_template[i], context)
            response_relevancy = await self.evaluate_response_relevancy(questions_template[i], answer, context)
            faithfulness_result = await self.evaluate_faithfulness(questions_template[i], answer, context)
            context_recall = await self.evaluate_context_recall(questions_template[i], answer, answers_template[i],
                                                                context)

            end_time = time.time()
            time_taken = end_time - start_time

            # # Store the results for this question in a dictionary
            result = {
                'question': questions_template[i],
                'ground_truth': answers_template[i],
                'context': context,
                'answer': answer,
                'context_precision': context_precision,
                'response_relevancy': response_relevancy,
                'faithfulness_result': faithfulness_result,
                'context_recall': context_recall,
                'temporal_information': is_temporal_res.dict(),  # Convert to dict for JSON serialization
                'time_taken': time_taken
            }

            results.append(result)
            print("Iteration " + str(i) + " took " + str(time_taken) + " seconds")

        with open("evaluation_results_t_with_llm.json", mode='w', newline='') as jsonfile:
            json.dump(results, jsonfile, indent=4)

    #Nicole^

    #nicole below
    async def get_dataset_preQRAG_llm(self, course_code: str):
        """
        Get dataset for multi-document LLM evaluation.
        
        Args:
            course_code (str): Course code to retrieve videos for.
        """
        
        # Retrieve the video ID and title mapping from database
        video_mapping = self.broker_service.get_video_id_title_mapping(course_code)
        
        print(f"Video mapping for course {course_code}: {video_mapping}")


        results = []  # This will store the results for all questions
                
        # Process each video ID in the array
                  
        for i in range(len(self.generic_questions)):
            start_time = time.time()
            # question = self.questions[i]
            question = "What was talked about at 23:00 in Sc1007_videolecture and did Lecture2_Sc1007 mention BFS?"

            json_results_llm = await self.chat_service.route_pre_qrag(user_query=question,video_map=video_mapping)

            print("Here is the json output: \n", json_results_llm)
            return


            
            # Step 1: Anchor Extraction and temporal check. Get the video title for reference and Timestamp if any, 
            # also map the title to the video id here. output =  {{"video_dis:"{video_id1:"...",vide_id2:"..."}},{{"Timestamps:"{"{video_id1_timestamp:"...",video_id2_timestamp:"..."}}"}
            #Step 2: Decide if Single or MultiDocs. If more than 1 video_dis in video_dis then multicdocs, else single docs.
            #Step 3: For single Docs, generte query variants into 2 query_variants. Then normal retrieval video_id, timestamp if any. For each query variant, retrieve the top 6 (sparse and dense) chunks, then do RRF top 6 from 12. Then generate the response with the Original query and chunks.
            #Step 4: For multi docs, generate query_variants into 2 query_variants. Then retrieve chunks based on that question for each video id. 
            #Step 5: For General Queries, rewrite the question into 2 query variants. Retrieve the top 6 (sparse and dense) chunks, then do RRF top 6 from 12. Then generate the response with the Original query and chunks.
            
            # Send the query and the video map to the LLM



            for video_id in video_mapping:

            # Step 1: check if the question requires single docs or multidocs query, video_id and title map
                question_checker = await self.chat_service.is_temporal_question(question)
                is_temporal = is_temporal_res.is_temporal
                timestamp = is_temporal_res.timestamp

                context = []
                answer = ""

                if is_temporal:
                    if timestamp:
                        # Step 3: Retrieve chunks based on the timestamp
                        retrieval_results, context = self.chat_service.retrieve_chunks_by_timestamp(video_id, timestamp)
                        answer = self.chat_service.generate_video_prompt_response(retrieval_results, question)
                    else:
                        # fallback if timestamp not extractable
                        retrieval_results, context = self.chat_service.retrieve_results_prompt_clean(video_id, question)
                        answer = self.chat_service.generate_video_prompt_response(retrieval_results, question)
                else:
                    retrieval_results, context = self.chat_service.retrieve_results_prompt_clean(video_id, question)
                    answer = self.chat_service.generate_video_prompt_response(retrieval_results, question)
                
                # TODO: Add evaluation logic here similar to other functions
                # For now, just print the results
                print(f"Question: {question}")
                print(f"Answer: {answer}")
                print(f"Context: {context}")
                print("-" * 50)


        

    #nicole ^



    async def get_dataset_pre_t(self, video_id):
        results = []  # This will store the results for all questions

        # Iterate through the questions and evaluate the answers
        for i in range(len(self.time_sensitive_questions)):
            retrieval_results, context = self.chat_service.retrieve_results_prompt(video_id, self.time_sensitive_questions[i])
            print(str(i) + " get_dataset_pre " + str(context))
            answer = self.chat_service.generate_video_prompt_response(retrieval_results, self.time_sensitive_questions[i])

            # Evaluate metrics
            context_precision = await self.evaluate_context_precision(self.time_sensitive_questions[i], self.time_sensitive_answers[i], context)
            response_relevancy = await self.evaluate_response_relevancy(self.time_sensitive_questions[i], answer, context)
            faithfulness_result = await self.evaluate_faithfulness(self.time_sensitive_questions[i], answer, context)
            context_recall = await self.evaluate_context_recall(self.time_sensitive_questions[i], answer, self.time_sensitive_answers[i],
                                                                context)

            # Store the results for this question in a dictionary
            result = {
                'question': self.time_sensitive_questions[i],
                'ground_truth': self.time_sensitive_answers[i],
                'context': context,
                'answer': answer,
                'context_precision': context_precision,
                'response_relevancy': response_relevancy,
                'faithfulness_result': faithfulness_result,
                'context_recall': context_recall
            }

            results.append(result)

        with open("evaluation_results_pre_t.json", mode='w', newline='') as jsonfile:
            json.dump(results, jsonfile, indent=4)

    async def get_dataset_naive_t(self, video_id):
        results = []  # This will store the results for all questions

        # Iterate through the questions and evaluate the answers
        for i in range(len(self.time_sensitive_questions)):
            retrieval_results, context = self.chat_service.retrieve_results_prompt_naive(video_id, self.time_sensitive_questions[i])
            print(str(i) + " get_dataset_naive " + str(context))
            answer = self.chat_service.generate_video_prompt_response(retrieval_results, self.time_sensitive_questions[i])

            # Evaluate metrics
            context_precision = await self.evaluate_context_precision(self.time_sensitive_questions[i], self.time_sensitive_answers[i], context)
            response_relevancy = await self.evaluate_response_relevancy(self.time_sensitive_questions[i], answer, context)
            faithfulness_result = await self.evaluate_faithfulness(self.time_sensitive_questions[i], answer, context)
            context_recall = await self.evaluate_context_recall(self.time_sensitive_questions[i], answer, self.time_sensitive_answers[i],
                                                                context)

            # Store the results for this question in a dictionary
            result = {
                'question': self.time_sensitive_questions[i],
                'ground_truth': self.time_sensitive_answers[i],
                'context': context,
                'answer': answer,
                'context_precision': context_precision,
                'response_relevancy': response_relevancy,
                'faithfulness_result': faithfulness_result,
                'context_recall': context_recall
            }

            results.append(result)

        with open("evaluation_results_naive_t.json", mode='w', newline='') as jsonfile:
            json.dump(results, jsonfile, indent=4)

    async def get_dataset_clean_naive_t(self, video_id):
        results = []  # This will store the results for all questions

        # Iterate through the questions and evaluate the answers
        for i in range(len(self.time_sensitive_questions)):
            retrieval_results, context = self.chat_service.retrieve_results_prompt_clean_naive(video_id, self.time_sensitive_questions[i])
            print(str(i) + " get_dataset_naive " + str(context))
            answer = self.chat_service.generate_video_prompt_response(retrieval_results, self.time_sensitive_questions[i])

            # Evaluate metrics
            context_precision = await self.evaluate_context_precision(self.time_sensitive_questions[i], self.time_sensitive_answers[i], context)
            response_relevancy = await self.evaluate_response_relevancy(self.time_sensitive_questions[i], answer, context)
            faithfulness_result = await self.evaluate_faithfulness(self.time_sensitive_questions[i], answer, context)
            context_recall = await self.evaluate_context_recall(self.time_sensitive_questions[i], answer, self.time_sensitive_answers[i],
                                                                context)

            # Store the results for this question in a dictionary
            result = {
                'question': self.time_sensitive_questions[i],
                'ground_truth': self.time_sensitive_answers[i],
                'context': context,
                'answer': answer,
                'context_precision': context_precision,
                'response_relevancy': response_relevancy,
                'faithfulness_result': faithfulness_result,
                'context_recall': context_recall
            }

            results.append(result)

        with open("evaluation_results_naive_clean_t.json", mode='w', newline='') as jsonfile:
            json.dump(results, jsonfile, indent=4)

    async def evaluate_context_precision(self, user_input: str, reference: str, retrieved_contexts: List[str]):
        context_precision = LLMContextPrecisionWithReference(llm=LangchainLLMWrapper(self.llm_evaluator))
        sample = SingleTurnSample(
            user_input=user_input,
            reference=reference,
            retrieved_contexts=retrieved_contexts,
        )
        result = await context_precision.single_turn_ascore(sample)
        return result

    async def evaluate_response_relevancy(self, user_input: str, response: str, retrieved_contexts: List[str]):
        sample = SingleTurnSample(
            user_input=user_input,
            response=response,
            retrieved_contexts=retrieved_contexts
        )

        evaluator_embeddings = AzureOpenAIEmbeddings(
            openai_api_version="2023-05-15",
            azure_deployment="text-embedding-ada-002",
            model="text-embedding-ada-002",
        )

        scorer = ResponseRelevancy(llm=LangchainLLMWrapper(self.llm_evaluator), embeddings=LangchainEmbeddingsWrapper(evaluator_embeddings))
        result = await scorer.single_turn_ascore(sample)
        print(result)
        return result

    async def evaluate_faithfulness(self, user_input: str, response: str, retrieved_contexts: List[str]):
        sample = SingleTurnSample(
            user_input=user_input,
            response=response,
            retrieved_contexts=retrieved_contexts
        )

        scorer = Faithfulness(llm=LangchainLLMWrapper(self.llm_evaluator))

        result = await scorer.single_turn_ascore(sample)
        print(result)
        return result

    async def evaluate_context_recall(self, user_input: str, response: str, reference:str, retrieved_contexts: List[str]):
        sample = SingleTurnSample(
            user_input=user_input,
            response=response,
            reference=reference,
            retrieved_contexts=retrieved_contexts
        )

        scorer = LLMContextRecall(llm=LangchainLLMWrapper(self.llm_evaluator))

        result = await scorer.single_turn_ascore(sample)
        print(result)
        return result

    #nicole (to map the course id to the video ids in that course)
    async def video_mapping(self, course_code: str):

        video_mapping = self.broker_service.get_video_id_title_mapping(course_code)
        print(f"Video mapping for course {course_code}: {video_mapping}")
        return video_mapping

async def main():
    service = ChatService()
    service2 = BrokerRepository()
    # video_id = "zwb6lqhpzl"
    print ("Evaluation stating......")

   
    # evaluator_service = EvaluatorService(chat_service=service)
    #await evaluator_service.get_dataset(video_id=video_id)
    # await evaluator_service.get_dataset_pre(video_id=video_id)
    # await evaluator_service.get_dataset_naive(video_id=video_id)
    # await evaluator_service.get_dataset_clean_naive(video_id=video_id)

    evaluator_service = EvaluatorService(chat_service=service, broker_service=service2)
    # await evaluator_service.get_dataset_t(video_id=video_id) #this is the non temporal pipeline that i used!
    # await evaluator_service.get_dataset_pre_t(video_id=video_id)
    # await evaluator_service.get_dataset_naive_t(video_id=video_id)
    # await evaluator_service.get_dataset_clean_naive_t(video_id=video_id)

    
    #nicole temporal and for generic
    # await evaluator_service.get_dataset_t_with_llm(video_id="zwb6lqhpzl")
    
    #still building this 
    await evaluator_service.get_dataset_preQRAG_llm(course_code="SC1177")  # Replace with your course code
    
    #mutlivideo(run thru all no question checker)
    # video_ids = await evaluator_service.video_mapping(course_code="SC1177")
    # await evaluator_service.get_dataset_mutlivid(video_ids=video_ids)



# Run the main function
if __name__ == '__main__':
    asyncio.run(main())
