import os
from dotenv import load_dotenv
from typing_extensions import TypedDict
from langchain_core.messages import AnyMessage
from typing import Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from agent.tools import tools
from langgraph.checkpoint.memory import MemorySaver
from langchain.output_parsers import XMLOutputParser
from langchain_core.prompts import ChatPromptTemplate
import json
from langchain_core.messages import RemoveMessage

load_dotenv()
os.environ["GROQ_API_KEY"]= os.getenv("GROQ_API_KEY")

class MessageState(TypedDict):
    messages:str
    instructions:Annotated[list[AnyMessage],add_messages]
    messages_history:Annotated[list[AnyMessage],add_messages]
    question_type:str
    temp_inst:str
    error:str
    status:str 
    response:str
    locations_history : Annotated[list[AnyMessage],add_messages]
    sent:bool
    previous_state:str
    user_response:str
    question:str
    user_question_type:str
    type_:str
    location:str
    previous_location:str
    


class build_graph():
    def __init__(self):

        t=tools()
        self.model=ChatGroq(model="qwen-2.5-32b")
        self.travel=t.travel
        self.speak=t.speak
        self.memory=MemorySaver()

        self.tools_list=[self.travel,self.speak]

        self.llm_with_tool=self.model.bind_tools(self.tools_list)

        self.builder=StateGraph(MessageState)
        self.builder.add_node("orchestrate",self.orchestrate)
        self.builder.add_node("user_response_fun",self.user_response)
        self.builder.add_node("clear_instruction",self.clear_instruction)
        self.builder.add_node("tool_calling_llm",self.tool_calling_llm)
        self.builder.add_node("tools", ToolNode(self.tools_list))
        self.builder.add_node("request_check",self.request_check)
        self.builder.add_node("response_message",self.response_message)
        self.builder.add_node("update_prev",self.update_prev)
        self.builder.add_conditional_edges(START,self.request_type,{"starting":"request_check","mid":"user_response_fun","end":"update_prev"})
        self.builder.add_conditional_edges("request_check",self.check_for_request,{"route":"clear_instruction","question":"response_message","end":"update_prev"})
        self.builder.add_conditional_edges("user_response_fun",self.question_answer_condition,{"wait":"update_prev","continue":"update_prev","location":"request_check"})
        self.builder.add_edge("update_prev",END)
        self.builder.add_edge("response_message",END)
        self.builder.add_edge("user_response_fun",END)
        self.builder.add_edge("clear_instruction","orchestrate")
        self.builder.add_conditional_edges("orchestrate",self.status_check,{"free":"tool_calling_llm","pending":"response_message"})
        self.builder.add_conditional_edges("tool_calling_llm",tools_condition,)
        self.builder.add_edge("tools","tool_calling_llm")

        # self.graph=self.builder.compile(checkpointer=self.memory)
        self.graph=self.builder.compile(checkpointer=self.memory)

    def update_prev(self,state=MessageState):
        return {"previous_state":"free","instructions":[RemoveMessage(id=m.id) for m in state["instructions"]],"response":""}

    def request_type(self,state=MessageState):
        if(state["type_"]=="starting"):
            return "starting"
        if(state["type_"]=="mid"):
            return "mid"
        return "end"

    def graph_workflow(self):
        return self.graph

    def request_check(self,state=MessageState):
        sys_message="""
        you are given with user_input, classify it into a 2 categories. 
        1. "route" if it is about traveling some where or to do some task
        2. "question" if it is a general question / chat / conversation

        response must be one word "route" or "question"
        """
        template = ChatPromptTemplate([
            ("system", sys_message),
            ("human", "user_input:{user_input}"),
        ])
        # print(state)
        chain = template | self.model
        answer = chain.invoke({"user_input":state["messages"][0].content})
        # print(f"question type: {answer.content}")
        return {"question_type":answer.content}

    def check_for_request(self,state=MessageState):
        sent=False
        status="free"
        if "sent" in state.keys():
            sent=state["sent"]
        if "status" in state.keys():
            status=state["status"]
        if sent==True and status=="free":
            return "end"
        if state["question_type"]=="route":
            return "route"
        else:
            return "question"

    def response_message(self,state=MessageState):
        status="free"
        # print(state)
        if "previous_state" in state.keys():
            status=state["previous_state"]
        sent=True
        if(state["question_type"]=="route" and status=="writing"):
            sent=False
         
        locations_history=state["locations_history"]
        task_history=state["messages_history"]
        # print(task_history)
        current_task=""
        if(len(task_history)>0):
            current_task=task_history[-1].content

        sys_message="""
        you are a robotic voice assistant, your task is to answer the question given by the user according to your current state, Location history and task history.
        your current status is {status} (if it is pending that means you are performing some task right now so return i am in the {current_task}, if free that means you are free to perform any task)
        locations history is {locations_history} (locations you have traveled so far, last one is the current location you are in if status is pending)
        task history is {task_history} (tasks you have completed so far, last one is the current task you are performing if status is pending)
        """

        template = ChatPromptTemplate([
            ("system", sys_message),
            ("human", "user_input:{user_input}"),
        ])
        # print(state)
        chain = template | self.model
        answer = chain.invoke({"current_task":current_task,"status":status,"locations_history":locations_history,"task_history":task_history,"user_input":state["messages"][0].content})
        return {"response":answer.content,"question_type":"question","sent":sent}

    

    def clear_instruction(self,state=MessageState):
        messages=state["instructions"]
        return {"instructions":[RemoveMessage(id=m.id) for m in messages]}
    def orchestrate(self,state=MessageState):
        parser = XMLOutputParser(tags=["task","route"])
        content = """
        # you are a orchestrate agent, your task is to plan the traveling route to complete that task. consider completing task for each path at a time.
        follow the rules:
        1. some times task will not be specified just output the path.
        2. always prefer starting from current location.
        3. choose locations only from this list (including spellings): ["current location","road","parking","park","waiting sofa","dining table","tv","kitchen","bedroom 3","bedroom 2","bedroom 1","store room","laundry","main door"]
        4. dont make any assumption about just do what is in the given prompt.
        5. just output task and route in json format such as [("task 1":task,"route":[start,end]),("task 2":task,"route":[start,end])] route must have 2 fields always
        """
        template = ChatPromptTemplate([
            ("system", content),
            ("human", "user_input:{user_input}"),
        ])
        # print(state)
        chain = template | self.model
        if("previous_location" in state.keys()):
            prev=state["previous_location"]
        else:
            prev="current location"
        # print(prev)
        answer = chain.invoke({"user_input":state["messages"][0].content,"previous_location":prev})
        print("#"*20)
        if(answer.content[:7]=="```json"):
            response=answer.content[7:-3]
        else:
            response=answer.content
        if response[0]=='{':
            response='['+response+']'

        print(response)
        last_route=json.loads(response)[-1]["route"]
        messages = state["instructions"]
        # for i in messages:
        #     print(i)
        # print(answer)
        return {"instructions": [response],"temp_inst":response, "locations_history": [last_route[-1]],"messages_history":[state["messages"][0].content],"previous_location":last_route[-1]}

    def status_check(self,state=MessageState):
        status=state["status"]
        previous_state="free"
        if "previous_state" in state.keys():
            previous_state=state["previous_state"]

        sent=False
        if "sent" in state.keys():
            sent=state["sent"]
        
        if sent==True and status=="free" and previous_state=="writing":
            status="free"
        
        elif sent==True and status=="writing" and previous_state=="pending":
            status="pending"

        elif sent==False and status=="free" and previous_state=="writing":
            status="free"

        elif sent==False and status=="writing" and previous_state=="writing":
            status="pending"
        
        else:
            status="free"

        return status

    def user_response(self,state=MessageState):
        sys_message1="""
        you are given with a question and a user response for that question. classify it into a 3 categories.
        1. wait (if the user asks you to wait for some time)
        2. move (if the work is done or user wants you to move)
        3. location (if user wants you to go to certain location to get the work done)
        your response must be one word "wait" or "move" or "location"
        """
        sys_message2="""
        you are given with some text/question you need to decide whether a person response is required for that text or not. classify it into a 2 categories.
        1. wait (if the text/question requires a person/user response or if the meaning of the text is about asking for a user action)
        2. move (if the text does not require a user response / if it only tells about the task it is performing)
        your response must be one word "wait" or "move"

        example:
        question: "I have arrived at bedroom 1. Please help me by taking the bat and giving it to me."
        answer: "wait" ( as the given question is about asking for a bat it needs a user action)

        question: I have arrived at the park.
        answer: "move" (as the given text is just describing its location it does not need a user action it is just informing the user)

        question: "make some coffee for me"
        answer: "wait"
        """

        if len(state["user_response"])>1:
            template = ChatPromptTemplate([
                ("system", sys_message1),
                ("human", "question:{question} user_response:{user_response}"),
            ])

            chain = template | self.model

            answer = chain.invoke({"question":state["question"],"user_response":state["user_response"]})
            # print(answer)
            if answer.content=="location":
                return {"user_question_type":"location","messages":[HumanMessage(content=state["user_response"])]}
            return {"user_question_type":answer.content}
        else:
            template = ChatPromptTemplate([
                ("system", sys_message2),
                ("human", "question:{question}"),
            ])

            chain = template | self.model

            answer = chain.invoke({"question":state["question"]})
            return {"user_question_type":answer.content}


    def question_answer_condition(self,state=MessageState):
        if(state["user_question_type"]=="wait"):
            return "wait"
        elif(state["user_question_type"]=="move"):
            return "continue"
        else:
            return "location"

    def tool_calling_llm(self,state=MessageState):
        if(len(state["locations_history"])>0):
            prev=state["locations_history"][-1].content
        else:
            prev="current location"

        sys_message ="""
        you are a robot voice assistant, you are task is to travel from one place to other place and speak according to the given tasks. select locations only from this list {"current location","road","parking","park","waiting sofa","dining table","tv","kitchen","bedroom 3","bedroom 2","bedroom 1","store room","laundry","main door"}.
        always follow given locations and dont miss any locations to travel.
        You can only travel, transfer, carry, clean and speak. So ask user to perform other task like (giving things to you, making some things for you) so that you can transfer according to the specified locations. first travel and then ask if there is any need of person involvement ( remember you can only travel, transfer, carry, clean and speak).
        try to speak like human always say what you are going to do, ask for requirements after reaching the location, travel every location as per the plan. dont make any tool calling errors."
        cover every task as given in the json input dont miss any go according to given plan.
        only travel locations that are mentioned in the json input.
        example:
        if user wants you to make a coffee. as you can only travel, transfer, carry, clean and speak. you should first travel to the kitchen, then ask if there is any one here to make the coffee for you , then travel / transfer as per the given instructions.
        
        """

        sys_msg=SystemMessage(content=sys_message)
        human_message=HumanMessage(content=state["temp_inst"])
        
        question = [sys_msg]+[human_message]
        try:
            answer = self.llm_with_tool.invoke(question)
            return {"instructions" : [answer],"status":"pending","sent":True,"previous_state":"pending"}
        except Exception as e:
            print("ERROR"*30)
            print(e)
            return {"error" : "please adjust the prompt and try again"}
    
    def status_on(self,thread_id):
        type_="starting"
        config={"configurable":{"thread_id":thread_id}}
        status="free"
        response=self.graph.stream({"type_":type_,"status":status},config=config,stream_mode="values")
        last_event=[event for event in response]

        return self.output(last_event)

    def response(self,message,name,thread_id,type_):
        config={"configurable":{"thread_id":thread_id}}
        messages=[HumanMessage(content=message,name=name)]
        # response=self.graph.invoke({"messages":messages})
        response=self.graph.stream({"type_":type_,"messages":messages,"status":"writing"},config=config,stream_mode="values")
        last_event=[event for event in response]
        # print(last_event)
        if last_event[-1]["question_type"]=="question":
            return [last_event[-1]["response"]]
        return self.output(last_event)

    def middle_response(self,question,user_response,name,thread_id,type_):
        config={"configurable":{"thread_id":thread_id}}
        response=self.graph.stream({"type_":type_,"question":question,"user_response":user_response,"status":"writing"},config=config,stream_mode="values")
        last_event=[event for event in response]
        # print(last_event)
        answer=[last_event[-1]["user_question_type"]]
        # print(answer)
        if answer[0]=="location":
            return [answer]+[self.output(last_event)]
        
        return [last_event[-1]["user_question_type"]]
        
    def output(self,last_event):
        last_chat=last_event[-1]["instructions"]


        # print(last_chat)
        AI_message=[i for i in last_chat if str(type(i))=="<class 'langchain_core.messages.ai.AIMessage'>"]
        Tool_message=[i for i in last_chat if str(type(i))=="<class 'langchain_core.messages.tool.ToolMessage'>"]
        tool_content=""
        for i in Tool_message:
            tool_content=i.content+"\n"
        process=""

        if(len(AI_message)==0):
            return "is there any thing you want me to do ?"
        # print(AI_message)
        # for i in AI_message:
        #     print(i)
        if "tool_calls" in AI_message[-1].additional_kwargs:
            AI_content=AI_message[-1].additional_kwargs["tool_calls"]
        else:
            AI_content=AI_message[-1].content
        with open("lastpossition.json", "r") as f:
            data = json.load(f)
        # print(data)
        try :
            data_to_send_list=[]
            for i in AI_content:
            #     print(i)
            #     print("$"*20)
                data_to_send={}
                if(i["function"]["name"]=="travel"):
                    # print(i["function"]["arguments"].split(",")[0].split(":")[1])
                    A = i["function"]["arguments"].split(",")[0].split(":")[1].replace('"', "")
                    B=i["function"]["arguments"].split(",")[1].split(":")[1].replace('"', "")
                    data_to_send['A']=data["current location"]
                    data_to_send['B']=data[B[1:-1]]
                    data_to_send_list.append(data_to_send)
                else:
                    data_to_send_list.append(json.loads(i["function"]["arguments"])["text"])
            # print(data_to_send_list)
            
            return data_to_send_list
        except Exception as e:
            return "please adjust the prompt and try again"
