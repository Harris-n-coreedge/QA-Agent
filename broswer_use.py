# from browser_use import Agent, ChatGoogle
# from dotenv import load_dotenv
# import asyncio
# import os
# load_dotenv()

# async def main():
#     llm = ChatGoogle(model="gemini-flash-latest")
#     # task = "Find the number 1 post on Show HN"
#     # task = "Go to the website https://www.w3schools.com, click on sign button and login with the following credentials: username: test@test.com, password: test and then click again sign button and give the error message"
#     task = "We are going to check a test case, Go to the website https://gdg.community.dev/, click on Login and then click on next if the it shows error 'Enter an email or phone number' then test case is passed otherwise it is failed"
#     # task = "we are going to check a test case, we will go to the website https://www.w3schools.com, click on sign button and login with the following credentials: username: abc@dd.com, password: 123 and then click again on sign in button and extract the error message and if error a message is displayed 'Invalid username or password' then test case is passed otherwise it is failed"
#     # task = "we are going to check a test case, we will go to the website https://supabase.com, click on sign button and login with the following credentials: username: abc@dd.com, password: 123 and then click again sign in button and extract the error message and if error message is which will appear for few seconds 'Invalid login credentials' then test case is passed otherwise it is failed"
#     # task = """we are going to check a test case, we will go to the website https://wisemarket.com.pk, 
#     # from left side menu click on 'Mobiles & Tablets' and then click on Mobile option,
#     # scroll down and click on 'Realme GT 7', click on its picture and then click on 'Add to Cart' button,
#     # click on "View Cart" button and then click on "Checkout" button,
#     # if a modal appears with a title 'Login to your wisemarket account' then test case is passed otherwise it is failed
#     # """
#     agent = Agent(task=task, llm=llm)
#     await agent.run()

# if __name__ == "__main__":
#     asyncio.run(main())
    