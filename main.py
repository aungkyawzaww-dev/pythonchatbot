from openai import OpenAI
from fastapi import FastAPI, Form, Request, WebSocket
from typing import Annotated
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os 
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()



client = OpenAI(
    api_key = os.getenv("OPENAI_API_KEY")
)


templates = Jinja2Templates(directory="templates")

# Moute static directory
app.mount("/static",StaticFiles(directory="static"),name="static")


chatlogs = [{
    "role":"system",
    "content":"You are a friend of DLT, \
        Also, you know everything general knowledge." # \ mean next new line
    }]

datas = []

# Text Generate
# => Template(http://127.0.0.1:8000/chat)

@app.get("/",response_class=HTMLResponse)
async def chatpage(request:Request):
    return templates.TemplateResponse(
        # request= request,name="layout.html"
        # request = request, name= "layout.html", context= {"datas":datas}  
        "layout.html",{"request":request, 'datas':datas} # get old datas
    ) 

#  Text Generate (Before Websocket )
# @app.post('/',response_class=HTMLResponse)
# async def chat(request:Request,userinput:Annotated[str,Form()]):
#     chatlogs.append({"role":"user","content":userinput})

#     datas.append(userinput)

#     completion = client.chat.completions.create(
#         model="gpt-3.5-turbo",
#         store = False, # ကိုယ်မေးတဲ့မေးခွန်းတွေကိုမှတ်ထားမလား True/မမှတ်ထားဘူးလာား False
#         messages = chatlogs,
#         temperature = 0.6 # .5 ( 0 to 2)

#     )

#     botresponse = completion.choices[0].message.content
#     chatlogs.append({"role":"assistant","content":botresponse})
#     datas.append(botresponse)

#     return templates.TemplateResponse(
#         # "layout.html",{"request":request, 'datas':datas}
#         request = request, name= "layout.html", context= {"datas":datas}

#     )


# => Text Generate (After WebSocket without streaming)
# exe1 
# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     while True:
#         userinput = await websocket.receive_text()
#         await websocket.send_text(userinput)


# # exe2 
# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     while True:
#         userinput = await websocket.receive_text()
#         # return userinput

#         chatlogs.append({"role":"user","content":userinput})

#         try:
#             completion = client.chat.completions.create(
#                 model="gpt-3.5-turbo",
#                 store = False, 
#                 messages = chatlogs,
#                 temperature = 0.6 
#             )

#             botresponse = completion.choices[0].message.content
#             await websocket.send_text(botresponse)

#             chatlogs.append({"role":"assistant","content":botresponse})

#         except Exception as err:
#             await websocket.send_text(f"Error Found: {str(err)}")
#             break


# => Text Generate (After WebSocket with streaming)
# exe3
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        userinput = await websocket.receive_text()

        chatlogs.append({"role":"user","content":userinput})

        fullresponse = ""

        try:
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                store = False, 
                messages = chatlogs,
                temperature = 0.6,
                stream = True,
            )

            for chunk in completion:
                botresponse = chunk.choices[0].delta.content
                if botresponse is not None:
                    fullresponse += botresponse
                    await websocket.send_text(str(botresponse))
            
            chatlogs.append({"role":"assistant","content":botresponse})

        except Exception as err:
            await websocket.send_text(f"Error Found: {str(err)}")
            break



# Image Generate
# => Template(http://127.0.0.1:8000/image)

@app.get("/image",response_class=HTMLResponse)
async def image(request:Request):
    return templates.TemplateResponse(
        # request = request, name= "image.html", context= {"data":data}
        request = request,name= "image.html"
    )

# @app.post('/image',response_class=HTMLResponse)
# async def generateimage(request:Request,userinput:Annotated[str,Form()]):

#     error = None
#     data = None

#     try:
#         completion = client.images.generate(
#             model="dall-e-2",
#             prompt=userinput,
#             size="512x512",
#             n=1,
#         )

#         botresponse = completion.data[0].url

#         if not completion.data or not botresponse:
#             raise ValueError("No image generated")

#         # updated data to the templage 
#         return templates.TemplateResponse(
            
#             # request = request, name= "image.html", context= {"data":botresponse}
#             "image.html",{"request":request, 'data':botresponse}

#         )
#     except Exception as e:
#         return templates.TemplateResponse(           
#             "image.html",{"request":request, 'data':data,"error":f"Error generation image:{str(e)}"}

#         )

# =>  Image Generate (After websocket)
@app.websocket("/image")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        userinput = await websocket.receive_text()


        try:
            completion = client.images.generate(
                model="dall-e-2",
                prompt=userinput,
                size="512x512",
                n=1,
            )

            botresponse = completion.data[0].url

            if not completion.data or not botresponse:
                raise ValueError("No image generated")

            await websocket.send_text(botresponse)

        except Exception as err:
            await websocket.send_text(f"Error Found: {str(err)}")
            break



#template example
# https://fastapi.tiangolo.com/advanced/templates/#using-jinja2templates 

# 22MA
# 5WS
# 6AP 
# 7OT