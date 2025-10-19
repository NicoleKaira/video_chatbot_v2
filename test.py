from videoLearnRAG.chatservice.chatservice import ChatService
import asyncio

async def test_query():
    cs = ChatService()
    result = await cs.query_evaluation("What are the video titles?", ["zwb6lqhpzl", "tg2fy923h1"], "SC1007")
    print(result)

# Run the async test
asyncio.run(test_query())




# import pkgutil
# import videoLearnRAG

# submodules = [m.name for m in pkgutil.walk_packages(videoLearnRAG.chatservice.__path__, videoLearnRAG.chatservice.__name__ + ".")]
# print(submodules)





