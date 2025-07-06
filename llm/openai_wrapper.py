from langchain.prompts import PromptTemplate
from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI

from IntelliReview.llm.base import LLMBase


class OpenAIWrapper(LLMBase):
    def __init__(self, api_key: str, model_name: str = "gpt-4o", temperature: float = 0.3):
        self.llm = ChatOpenAI(
            openai_api_key=api_key,
            model_name=model_name,
            temperature=temperature
        )
        self.prompt = PromptTemplate.from_template("""
You are a very experienced software engineer performing a thorough code review on the following GitHub pull request diff:

{diff}

Please provide detailed, constructive review comments including:
- Potential bugs or logical errors
- Code style and formatting issues
- Best practices violations
- Suggestions for improving readability, performance, or security
- Anything unusual or risky

Do NOT just say 'No issues found' unless the code is absolutely perfect.
        """)

    def invoke(self, input: dict) -> BaseMessage:
        chain = self.prompt | self.llm
        return chain.invoke(input)
