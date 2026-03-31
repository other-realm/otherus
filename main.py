#!/usr/bin/env python3
from functools import partial
from math import log
import re
from tkinter.font import names
from turtle import home, onclick
from authlib.common.encoding import json_dumps, json_loads
from click import prompt
from httpx import delete
from matplotlib import colors
from sympy.abc import F
from custom_sub_pages import custom_sub_pages, protected 
from typing import Text, TypedDict
import random
import uuid
import numpy as np
import datetime, os
from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import Request
from starlette.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from nicegui import events, app, ui, binding
import pandas as pd
import logging
import time
from typing import Optional
import nicegui as ng
from dotenv import load_dotenv
import redis
from redis.commands.json.path import Path
import redis.commands.search.aggregation as aggregations
import redis.commands.search.reducers as reducers
from redis.commands.search.field import TextField, NumericField, TagField
from redis.commands.search.index_definition import IndexDefinition, IndexType
from redis.commands.search.query import NumericFilter, Query
from datetime import datetime
import matplotlib
import matplotlib.pyplot as plt
import json
import base64
# import theme
# import home_page
load_dotenv('.env')
app.add_middleware(SessionMiddleware,
                     secret_key=os.getenv('random_secret'),
                     session_cookie="recession",
                     https_only=False)
GOOGLE_CLIENT_ID = os.getenv("client_id")
GOOGLE_CLIENT_SECRET = os.getenv("client_secret")
os.environ['NICEGUI_REDIS_URL']='redis://admin:'+os.getenv('redis_password')+'@10.0.0.90:6379'
os.environ['NICEGUI_REDIS_KEY_PREFIX']='otherus:'
app.storage.redis= redis.Redis(host="10.0.0.90",username='admin',password=os.getenv('redis_password'), port=6379, decode_responses=True)
r=app.storage.redis
oauth = OAuth()
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    client_kwargs={
        'scope': 'openid email profile',
        'redirect_uri': 'http://localhost:8086/auth'
    },
    authorize_state=os.getenv('random_secret')
) 
# @app.get('/login')
# async def login(request):
#     url=f"https://accounts.google.com/o/oauth2/auth?client_id={GOOGLE_CLIENT_ID}&redirect_uri={os.getenv('REDIRECT_URI')}&response_type=code&scope=openid%20email%20profile&state={os.getenv('random_secret')}"
#     print(url,'\n')
#     ui.button('Login with Google',on_click=lambda: ui.navigate.to(url)) 
#     # return await oauth.google.authorize_redirect(request, request.url_for('google_oauth'))
def _enter(e: events.GenericEventArguments):
    if e.args['shiftKey']:
        ui.notify('shift enter')
    else:
        ui.notify('enter')
@ui.page("/login")
async def login(request: Request):
    url = request.url_for('google_oauth')
    return await oauth.google.authorize_redirect(request, url) # pyright: ignore[reportOptionalMemberAccess]
async def loginred(request:Request):
    return RedirectResponse('/login')
@ui.page('/')
async def main(request: Request):
    user_info = app.storage.user.get('user_info', {})
    url =  await ui.run_javascript(f'new URL(window.location.origin)',timeout=10)
    # print('user:'+str(user_info['sub']))
    with ui.header(elevated=True).style('background-color: #000080').classes('justify-between'):
        ui.button(on_click=lambda: left_drawer.toggle(), icon='menu').tooltip('Menu')
        with ui.button(on_click=lambda: ui.navigate.to('/')):
            ui.image('https://www.otherrealm.org/themes/otherrealm/img/About.png').classes('rounded-full w-8')
            ui.tooltip('Home')
        ui.button('Color 🤷', on_click=lambda: (ui.navigate.to('/color_guess'),left_drawer.hide())).tooltip('Color Tests')
        ui.button(icon='logout', on_click=lambda: ui.navigate.to(url+'logout', new_tab=False)).tooltip('Logout')
        # ui.button(on_click=lambda: right_drawer.toggle(), icon='menu')
    with ui.left_drawer(value=False,fixed=True,top_corner=None, bottom_corner=False).style('background-color: #d7e3f4') as left_drawer:
        ui.button('🏠', on_click=lambda: (ui.navigate.to('/'),left_drawer.hide())).tooltip('Home')
        ui.button('Color 🤷', on_click=lambda: (ui.navigate.to('/color_guess'),left_drawer.hide())).tooltip('Collor Tests')
        ui.button('Number Test', on_click=lambda: (ui.navigate.to('/live_studies'),left_drawer.hide())).tooltip('Tests')
        ui.button('Test Results 📊', on_click=lambda: (ui.navigate.to('/study_results'),left_drawer.hide())).tooltip('Results')
        ui.button(icon='people', on_click=lambda: ui.navigate.to('/search_people')).tooltip('Find People')
        ui.button('Profile',on_click=lambda: (ui.navigate.to('/profile'),left_drawer.hide())).tooltip('IC Profile')
        ui.button('Account',on_click=lambda: (ui.navigate.to('/account'),left_drawer.hide())).tooltip('Account')
    with ui.footer(fixed=False).style('background-color: #000080'):
        footerContent="""
        <div class="footer center clearBoth">
            <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/" id="copyright" rel="license" title="You have the right to copy for non-commercial use; just make attribution to The Other Realm and make all changes publicly available">
                <img alt="Creative Commons License" class="cc" src="https://i.creativecommons.org/l/by-nc-sa/4.0/88x31.png" style="display: inline;margin: auto;border-width:0;" title="You have the right to copy for non-commercial use; just make attribution to The Other Realm and make all changes publicly available">
                Content:
            </a>
            <a href="https://otherrealm.org" title="Copyright Other Realm LLC">©
                <span id="year">2026</span>
                The Other Realm
                <br>
            </a>
            <a href="https://github.com/other-realm/otherus" title="Link to github repository"><img alt="Gnu AFFERO  Public License" class="gpl" src="https://www.gnu.org/graphics/agplv3-155x51.png" style='display: inline;margin: auto;'>Code is licensed under the GNU Afferō General Public License</a> - 
            <a href="/privacy_policy" title="Privacy Policy">Privacy Policy</a>
        </div>
            """
        ui.html(footerContent,sanitize=False)
    ui.add_head_html("""
            <link rel="stylesheet" type="text/css" href="/static/otherrealm.css">
            <script src="https://accounts.google.com/gsi/client" async></script>
            <script src="/static/otherrealmFunctions.js"></script>
        """)
    app.add_static_files('/static', 'static')
    if _is_valid(user_info):
        r.json().set('nice_user:'+str(user_info['sub'])+':login:', Path.root_path(),user_info)
        r.json().set('nice_user:'+str(user_info['sub'])+':sub', Path.root_path(),user_info['sub'])
        ui.sub_pages({
            '/':home_page,
            '/home':home_page,
            '/live_studies':live_studies,
            '/study_results':study_results,
            '/color_guess':color_guess,
            '/profile':survey,
            '/account':account,
            '/search_people':search_people,
            '/view_profile/{id}':view_profile,
            '/privacy_policy':privacy_policy,
            '/logout':logout,
            '/test':test,
        },data={"request":request}).classes('full-width row wrap justify-start items-start content-start')
        return None
    else:
        app.storage.user.pop('user_info', None)
        ui.sub_pages({
            '/':home_page,
            '/home':home_page,
            '/live_studies':home_page,
            '/study_results':home_page,
            '/profile':home_page,
            '/account':home_page,
            '/search_people':home_page,
            '/privacy_policy':privacy_policy,
            '/view_profile':home_page,
            '/logout':logout,
            '/test':test,
        },data={"request":request}).classes('full-width row wrap justify-start items-start content-start')
        return None
async def logout(request: Request):
    url = ui.run_javascript(f'new URL(window.location.origin)')
    with ui.button('Logout', on_click=lambda: ui.navigate.to(url+'logout', new_tab=False)):
        app.storage.user['user_info']['exp'] =0
        app.storage.user['user_info']['aud'] =''
        app.storage.user['user_info']['iss'] =''
        app.storage.user['user_info']['email_verified'] =False
        app.storage.user.pop('user_info', None)
        print(_is_valid(app.storage.user.get('user_info', {})))
        return ui.navigate.to('/')
    ui.navigate.reload()
# async def handle_click(e: events.ClickEventArguments):
#     e.sender.disable()
#     await compute.refresh()
#     e.sender.enable()
async def updateRandomGlobal():
    if 'randNum' not in app.storage.general:
        app.storage.general['randNum']=float(uuid.uuid4().int%1000)
    if 'guessCount' not in app.storage.general:
        app.storage.general['guessCount']=0
    if 'combinedNumber' not in app.storage.general:
        app.storage.general['combinedNumber']=False
    if 'combinedUserNumber' not in app.storage.general:
        app.storage.general['combinedUserNumber']=False
    if app.storage.general['combinedNumber']:
        combinedNumKey='combined_number:'+datetime.now().strftime('%Y-%m-%d_%H-%M-%S-%f')
        r.json().set('global:'+combinedNumKey, Path.root_path(),{
            "datetime":str(datetime.now().strftime('%Y%m%d%H%M%S%f')),
            "combined_guess_number":app.storage.general['combinedNumber'],
            "number_of_guesses":app.storage.general['guessCount'],
            "combined_user_number":app.storage.general['combinedUserNumber'],
            "target_number":app.storage.general['randNum']})
    app.storage.general['randNum']=float(uuid.uuid4().int%1000)
    app.storage.general['guessCount']=0
    app.storage.general['combinedNumber']=False
    app.storage.general['timestamp']=str(datetime.now().strftime('%Y%m%d%H%M%S%f'))
    print('general: ',app.storage.general['randNum'])
counter = {'value': 0}
# globalTimer=app.timer(.1, lambda: counter.update(value=counter['value'] + .1))
async def save_user_info(user_info):
    if user_info['user_info']['sub']:
        print(user_info)
        user_id='user_info:'+str(user_info['user_info']['sub'])
        r.json().set(user_id,Path.root_path(),{user_info})
globalTimer=app.timer(60, updateRandomGlobal)
async def home_page(request: Request):
    user = app.storage.user.get('user_info', {})
    url = await ui.run_javascript(f'new URL(window.location.origin)',timeout=10)
    print('home',_is_valid(user),url)
    if _is_valid(user)!=True:
        with ui.button('', on_click=lambda: ui.navigate.to(url+'login', new_tab=False)):
            ui.label("Click to login")
    if _is_valid(user):
        ui.label(f'Welcome {app.storage.user['user_info']['name'] or app.storage.user['user_info']['email']}!')
        with ui.button('', on_click=lambda: ui.navigate.to(url+'logout', new_tab=False)):
            ui.label("Click to logout")
@app.get('/auth')
async def google_oauth(request: Request) -> RedirectResponse:
    try:
        print(request)
        user_info = (await oauth.google.authorize_access_token(request)).get('userinfo', {}) # pyright: ignore[reportOptionalMemberAccess]
        if _is_valid(user_info):
            app.storage.user['user_info'] = user_info
            print('User info:',user_info)
            request.session['user_info'] = app.storage.user
    except (OAuthError, Exception):
        logging.exception('could not authorize access token')
    return RedirectResponse('/color_guess')
def _is_valid(user_info: dict) -> bool:
    if user_info:
        try:
            return all([
                int(user_info.get('exp', 0)) > int(time.time()),
                user_info.get('aud') == GOOGLE_CLIENT_ID,
                user_info.get('iss') in {'https://accounts.google.com', 'accounts.google.com'},
                str(user_info.get('email_verified')).lower() == 'true',
            ])
        except Exception:
            return False
    else:
        return False
async def account():
    ui.page_title('Other Us-Account')
    ui.button("Delete Account", on_click=del_account)
async def del_account():
    savedData=r.scan_iter('nice_user:'+str(app.storage.user['user_info']['sub'])+'*')
    savedProfileData=r.scan_iter('user_profile:'+str(app.storage.user['user_info']['sub'])+'*')
    results=[]
    for i, doc in enumerate(savedData):
        resu=r.json().delete(doc)
    for i, doc in enumerate(savedProfileData):
        resu=r.json().delete(doc)
    app.storage.user.pop('user_info', None)
    return ui.navigate.to('/')
@ui.refreshable
async def updateRandomUser(genT, sub):
    app.storage.user['knowOrGuess']=float((uuid.uuid4().int%100)/100)
    local_rand=str(app.storage.general['randNum'])
    with genT:
        if app.storage.user['knowOrGuess']<.4:
            print('general...: ',app.storage.general['randNum'])
            genT.set_text('You recived the #: '+local_rand+', enter it 👇')
            genT.set_visibility(True)
        else:
            genT.set_text('Enter Your Guess (less than 1000) Here👇')
            print('new knowOrGuess',counter['value'],app.storage.user['knowOrGuess'])
    with sub:
        sub.enable()
async def updateGuess(guess):
    try:
        app.storage.user['userGuess']=guess.value
        app.storage.general['guessCount']=app.storage.general['guessCount']+1
        if app.storage.general['combinedNumber']:
            app.storage.general['combinedNumber']=(float(app.storage.general['randNum'])+float(app.storage.user['userGuess']))/2
            app.storage.general['combinedUserNumber']=(float(app.storage.user['userGuess']))
        else:
            app.storage.general['combinedNumber']=(float(app.storage.general['randNum'])+float(app.storage.general['combinedNumber'])+float(app.storage.user['userGuess']))/3
            app.storage.general['combinedUserNumber']=(float(app.storage.general['combinedUserNumber'])+float(app.storage.user['userGuess']))/2
        print('Submitted guess',app.storage.user['userGuess']," : ",app.storage.general['guessCount']," : ",app.storage.general['randNum'], ' : ',app.storage.general['combinedNumber'])
        userkey='guess:'+str(app.storage.user['user_info']['sub'])+':count'+':'+datetime.now().strftime('%Y-%m-%d_%H-%M-%S-%f')
        r.json().set(userkey, Path.root_path(),{'knowOrGuess':app.storage.user['knowOrGuess'],'guess_value':app.storage.general['guessCount'],'guess':guess.value})
    except Exception as ep:
        print('<h1>Error: '+str(ep)+'</h1>')
        return RedirectResponse('/')
async def live_studies():
    ui.page_title('Other Us-Live Studies')
    if 'userGuess' not in app.storage.user:
        app.storage.user['userGuess']=0
    if 'knowOrGuess' not in app.storage.user:
        app.storage.user['knowOrGuess']=float((uuid.uuid4().int%100)/100)
    with ui.column(align_items='center'):
        ui.html("<h1 class='center'>What do you think the target # that some people have received is?</h1><br>",sanitize=False)
        genT=ui.label('')#
        guess=ui.input(placeholder="Enter Guess <1000 Here",validation=lambda value: 'Please only enter #s less than 1000' if not ((str(value).isdigit() and int(value)>=0) and int(value)<1000) else None).props('clearable').classes('row justify-center items-center, makeBig')
        guess.on('keypress.enter',partial(updateGuess,guess.bind_value(guess,'value')))
        # uG=ui.label(guess.value).bind_text(guess,'value',strict=False)
        sub=ui.button('Submit Guess',on_click=(partial(updateGuess,guess.bind_value(guess,'value')))) #.bind_enabled(app.storage.general,'randNum')
        sub.on_click(lambda:sub.disable())
        uiT=ui.timer(60,partial(updateRandomUser,genT,sub))
        genT.classes('makeBig')#.bind_visibility(float(app.storage.user['knowOrGuess'])<0.4,strict=False)
        kOG=ui.label(app.storage.user['knowOrGuess']).bind_text(uiT,'uiTimer',strict=False).bind_text(app.storage.user,'knowOrGuess')
        kOG.text=str(app.storage.user['knowOrGuess'])
        ui.link('Study Results','/study_results')
    await ui.context.client.connected()
async def color_guess():
    ui.page_title('Guess the Color')
    colors=['red','orange','yellow','green','blue','purple','white','black']
    svg='''
    <svg viewBox="0 0 1 1" width="100%"  height="100%"  preserveAspectRatio="none meet" xmlns="http://www.w3.org/2000/svg">
        <rect x='0' y='0' width="100%" height="50%" fill="purple"></rect>
        <a href="#red"><rect x='0' y='50%' width="25%" height="25%" fill="red"></rect>        </a>
        <a href="#orange"><rect x='25%' y='50%' width="25%" height="25%" fill="orange"></rect></a>
        <a href="#yellow"><rect x='50%' y='50%' width="25%" height="25%" fill="yellow"></rect></a>
        <a href="#green"><rect x='75%' y='50%' width="25%" height="25%" fill="green"></rect>    </a>
        <a href="#blue"><rect x='0' y='75%' width="25%" height="25%" fill="blue"></rect>       </a>
        <a href="#purple"><rect x='25%' y='75%' width="25%" height="25%" fill="purple"></rect>   </a>
        <a href="#white"><rect x='50%' y='75%' width="25%" height="25%" fill="white"></rect>    </a>
        <a href="#black"><rect x='75%' y='75%' width="25%" height="25%" fill="black"></rect>    </a>
    </svg>
    '''
    ui.add_css('''
    svg {  
      position: fixed;  
      top: 0;  
      left: 0;  
      width: 100vw;   /* Fill viewport width */  
      height: 100vh;
    }
    .h-full {
        width: 100%;
        height: 100%;
    }
    ''')
    ui.html(svg,sanitize=False).classes('h-full')
    ui.html(colors[uuid.uuid4().int%8],sanitize=False).classes('h-full')
async def study_results():
    ui.add_css('''
    svg {
        position: initial;
        top: initial;
        left: initial;
        width: initial;
        height: initial;
    }
    .h-full {
        width: 100%;
        height: 100%;
    }
    ''')
    ui.page_title('Other Us-Results')
    with ui.column(wrap=True,align_items='center').classes('w-full'):
        ui.html('<h1>Study Results 📊</h1><div class="center">',sanitize=False)
        with ui.matplotlib(figsize=(10, 6)).figure as fig:
            savedData=r.scan_iter('global:combined_number:*')
            results=[]
            for i, doc in enumerate(savedData):
                resu=r.json().get(doc)
                if not isinstance(resu['target_number'], bool): # pyright: ignore[reportOptionalSubscript]
                    results.append(dict(r.json().get(doc)))
            df=pd.DataFrame(results,columns=['datetime','combined_guess_number','number_of_guesses','combined_user_number','target_number'])
            df.plot(x='datetime', y=['combined_guess_number','combined_user_number','target_number'], xlabel='Guesses', kind='line', ax=fig.gca(),rot=35).tick_params(bottom=True,labelbottom=True)
            ui.table.from_pandas(df)
            fig.autofmt_xdate()
            fig.tight_layout(pad=2.0)
        ui.html('</div>',sanitize=False)
def del_url(url,idn,container,row):
    try:
        url.pop(idn)
        container.remove(row)
    except Exception as e:
        print('Error removing url: ',e)
        container.remove(row)
def add_url(container,form_name,idn=None,ex_url=None):
    with container:
        with ui.row(wrap=False) as row:
            if(idn==None):
                idn=form_name['urls']['value'].__len__()
            ui.button('Save', on_click=lambda: form_name['urls']['value'].append(url.value))
            url=ui.input(placeholder='Social media/other interesting links',value=ex_url).bind_value(form_name['urls']['value'],str(idn),strict=False)
            ui.button('Remove', on_click=lambda:del_url(form_name['urls']['value'],idn,container,row))
def add_2_slidders(container,topic,other):
    for slider_data in topic:
        # print(form_name,topic,slider_data)
        with container:
            with ui.grid(columns='7.5fr 1fr 7.5fr 1fr 1fr 7.5fr 1fr').classes('w-full gap-0'):
                ui.html('<b>'+topic[slider_data]['label']+'</b>',sanitize=False).classes
                ui.label('Have:')
                slider_ui1=ui.slider(min=0, max=100, step=1, value=50).bind_value(topic[slider_data],'have',strict=False)
                ui.label().bind_text_from(slider_ui1,'value',lambda v: f'{v}% ')
                ui.label('Want:')
                slider_ui2=ui.slider(min=0, max=100, step=1, value=50).bind_value(topic[slider_data],'want',strict=False)
                ui.label().bind_text_from(slider_ui2,'value',lambda v: f'{v}%')
            ui.separator()
    with container:
        ui.html('<b>'+other['label']+'</b>',sanitize=False)
        other_ui=ui.editor(placeholder="Something else...").bind_value(other,'value',strict=False)
        ui.separator()
    return container
def add_slidder(container,topic,other):
    for slider_data in topic:
        # print(form_name,topic,slider_data)
        with container:
            with ui.grid(columns='10fr 18fr 1fr').classes('w-full gap-0'):
                ui.html('<b>'+topic[slider_data]['label']+'</b>',sanitize=False)
                slider_ui=ui.slider(min=0, max=100, step=1, value=50).bind_value(topic[slider_data],'value',strict=False)
                ui.label().bind_text_from(slider_ui,'value',lambda v: f'{v}%')
            ui.separator()
    with container:
        ui.html('<b>'+other['label']+'</b>',sanitize=False)
        other_ui=ui.editor(placeholder="Something else...").bind_value(other,'value',strict=False)
        ui.separator()
    return container
async def savePhoto(e: events.UploadEventArguments,icq,button: ui.button=None):
    if(e):
        file_bytes = await e.file.read()
        image=base64.b64encode(file_bytes)
        image=image.decode('utf-8')
        print('Picture: ',image.__len__)
        icq['profile_image']['src']=image
    else:
        icq['profile_image']['src']=''
        print(e)
        loadPhoto.refresh()
    return icq
@ui.refreshable
async def loadPhoto(icq):
    if icq['profile_image']['src']!='':
        delete_me=ui.button('❌',on_click=lambda: savePhoto(None,icq))
        photo=ui.image('data:image/png;base64,'+icq['profile_image']['src']).style('max-width:400px;width:100%').classes('wide-input').bind_visibility(delete_me,"content",strict=False)
    else:
        ui.html("<span style='color:red;'>(be sure to click the 👇<i class='q-icon notranslate material-icons' style='color:#5898D4' aria-hidden='true' role='img'>cloud_upload</i> icon in the upper right once you have selected the image (Max size<6MB)):</style><br>",sanitize=False).classes('wide-input')
        photo=ui.upload(on_upload=lambda e: savePhoto(e,icq), on_rejected=lambda: ui.notify('Unfortunately your image was rejected, probably it is too big (Max<≈6MB)'),max_file_size=6_000_000).props('accept=.jpg,.png,.gif').classes('wide-input')
    return photo
async def save_me(sub,icq):
    r.json().set(sub+':icq', Path.root_path(),icq)
# @ui.refreshable
async def survey():
    sub=app.storage.user['user_info']['sub']
    # print('icq test: ',sub,r.json().get('user:'+sub+':sub'))  #  print('icq test: ','user'+app.storage.user['user_info']['sub'])
    # if (r.json().get('user:'+sub+':icq')!=None and r.json().get('user:'+sub+':sub')!=None):
    #     app.storage.user['user_info']['icq']=r.json().get('user:'+sub+':icq')
    # else:
    r.json().set('user_profile:'+sub+':icq', Path.root_path(),{
        "name":{"type":"input","label":"Your name, as you like to be known:","value":""},
        "id":sub,
        "profile_image":{
            "type":"image",
            "label":"Profile Picture (be sure to click the <i class='q-icon notranslate material-icons' aria-hidden='true' role='img'>cloud_upload</i> icon):",
            "src":"",
        },
        "urls":{
            "type":"editable_input_array",
            "label":"Do you have any social media or other interesting links to share (ex. https://ic.org/directory/..)?",
            "value":[]
        },"transhumanist_ideas":{
            "type":"editor",
            "label":"What transhumanist ideas do you want to work on together and test for their efficacy?</h2>  (ex: quantum entanglement, testing or refuting current claims of telepathy; use of an array of interconnected assembloids as an organic living server that interfaces with an EEG/TMS system, extra…)",
            "value":""},
        "crazy_ideas":{"type":"editor","label":"","value":""},
        "video_series":{"type":"radio","label":"","value":["Yes", "No", "Maybe"]},
        "wants":{
            "type":"slider_group",
            "label":"How much do these social qualities factor into the search for a community?",
            "other":{"label":"Something else:","value":""},
            "items":{
                "deep_conver":{"label":"Deep conversation","value":50},
                "shared_challenges":{"label":"Shared challenges","value":50},
                "shared_passions":{"label":"Shared passions","value":50},
                "shared_personality":{"label":"Shared personality","value":50},
                "shared_skills":{"label":"Shared skills and knowledge","value":50},
                "physical_closeness":{"label":"Physical closeness/touch between people","value":50},
                "complementary_skills":{"label":"Complementary skills and knowledge","value":50},
                "different_challenges":{"label":"Different challenges","value":50},
                "different_passions":{"label":"Different passions","value":50},
                "range_of_personalities":{"label":"A range of personalities","value":50},
                "separate_personal_space":{"label":"Separate personal space","value":50},
                "common_spaces_people_naturally_regularly_convene_in":{"label":"Common spaces that people naturally regularly convene in","value":50},
                "set_structured_time_together":{"label":"Set structured time together \n(i.e. planed events/meetings or community dinners)","value":50},
            }
        },
        "skills":{
            "type":"2_slider_group",
            "other":{"label":"Something else:","value":""},
            "label":"What skills do you currently have or want to acquire more of?",
            "items":{
                "ai_machine_learning":  {"label":"AI and Machine Learning ","have":50,"want":50},
                "bioengineering":       {"label":"Bioengineering","have":50,"want":50},
                "business":             {"label":"Business","have":50,"want":50},
                "community_building":   {"label":"Community Building","have":50,"want":50},
                "electronics":          {"label":"Electronics","have":50,"want":50},
                "medicine":             {"label":"Medicine","have":50,"want":50},
                "robotics":             {"label":"Robotics","have":50,"want":50},
                "microbiology":         {"label":"Microbiology","have":50,"want":50},
                "neuroscience":         {"label":"Neuroscience","have":50,"want":50},
                "education":            {"label":"Teaching/Learning","have":50,"want":50},
                "government":           {"label":"Government","have":50,"want":50},
                "quantum_physics":      {"label":"Quantum physics","have":50,"want":50},   
                "construction":         {"label":"Sustainable construction","have":50,"want":50},   
            }
        },
        "sharing":{
            "type":"slider_group",
            "other":{"label":"Something else:","value":""},
            "label":"Are you comfortable sharing (Multiple people in the same location at the same time or using the same thing, possibly at different times):",
            "items":{
                "food":{"label":"Food","value":50},
                "a_kitchen":{"label":"A kitchen","value":50},
                "dishes_utensils":{"label":"Dishes/utensils","value":50},
                "appliances":{"label":"Appliances","value":50},
                "a_computer_laptop":{"label":"A computer/laptop","value":50},
                "smartphone":{"label":"A smartphone","value":50},
                "cloths":{"label":"Cloths","value":50},
                "shop_lab_equipment":{"label":"Shop/Lab equipment","value":50},
                "consumable_materials":{"label":"Consumable materials (ex. TP, soap, cleaning supplies, ex.)","value":50},
                "house":{"label":"A house","value":50},
                "bedroom":{"label":"A bedroom","value":50},
                "bathroom":{"label":"A bathroom","value":50},
                "shower":{"label":"A shower","value":50},
                "bed":{"label":"A Bed","value":50},
                "a_life":{"label":"A Life Together","value":50},
            }
        },
        "current_location":{
            "type":"map",
            "label":"Your current Location (can be as general or specific as you like)",
            "placed":False,
            "coordinates":{"lat":42.3676371,"lng":-72.5054855}
        },
        "potential_locations":{
            "type":"editor",
            "label":"Do you know any locations that we should check out as a possible location where we could start working on things together in person?",
            "value":""
        },
    },nx=True)
    app.storage.user['user_info']['icq']=r.json().get('user_profile:'+sub+':icq')
    icq=app.storage.user['user_info']['icq']
    # print('new icq: ',icq)
    # print(icq)
    with ui.column(wrap=True, align_items='center').classes('wide-input'):
        ui.html('<h1 class="center-title">Intentional Community Profile</h1><p><em>Please</em>🥺<em>fill this out so we can all connect with the right people and work on cool projects together</em></p><p class="aligncenter">[Data is saved automatically unless there is a button that says "save"]</p>',sanitize=False).classes('wide-input')
        ui.html('<h2>Your name as you like to be known:</h2>',sanitize=False).classes('wide-input')
        name=ui.input(placeholder="Your name as you like to be known").bind_value(icq['name'],'value',strict=False).classes('wide-input')
        ui.html("<h2>Profile Picture</h2>",sanitize=False).classes('wide-input')
        with ui.column(wrap=True, align_items='center').classes('wide-input'):
            photo=await loadPhoto(icq)
        
        ui.html('<h2>Do you have any social media or other interesting links to share?</h2>',sanitize=False).classes('wide-input')
        container = ui.element('div').classes('aligncenter, wide-input')
        for i, url in enumerate(icq['urls']['value']):
            add_url(container,icq,i,url)
        ui.button('Add url', on_click=partial(add_url,container,icq,'')).classes('wide-input')

        with container:
            ui.html('<h2>What transhumanist ideas do you want to work on together and test for their efficacy?</h2>  (ex: testing or refuting current claims of telepathy; use of an array of interconnected assembloids as an organic living server that interfaces with an EEG/TMS system; quantum entanglement, extra…)',sanitize=False).classes('wide-input')
            transhumanist_ideas=ui.editor(placeholder="Your ideas here...").bind_value(icq['transhumanist_ideas'],'value',strict=False).classes('wide-input')
            ui.html('<h2>What other far-out-there crazy ideas are you wanting to collaborate on?</h2>',sanitize=False).classes('wide-input')
            crazy_ideas=ui.editor(placeholder="Your other ideas here...").bind_value(icq['crazy_ideas'],'value',strict=False).classes('wide-input')
        
        ui.html('<h2>Are you interested in collaborating on a video series that documents/dramatizes the creation of this community?</h2>',sanitize=False).classes('wide-input')
        video_series=ui.radio(['Yes', 'No', 'Maybe']).bind_value(icq['video_series'],'value',strict=False).classes('wide-input')

        ui.html('<h2>What skills do you currently have and how much do you want to learn more?</h2>',sanitize=False).classes('wide-input')
        container = ui.element('div').classes('wide-input')
        add_2_slidders(container,icq['skills']['items'],icq["skills"]['other'])
        
        ui.html('<h2>'+icq['wants']['label']+'</h2>',sanitize=False).classes('wide-input')
        container = ui.element('div').classes('wide-input')
        add_slidder(container,icq['wants']['items'],icq["wants"]['other'])
        
        ui.html('<h2>'+icq['sharing']['label']+'</h2>',sanitize=False).classes('wide-input')
        container = ui.element('div').classes('wide-input')
        add_slidder(container,icq['sharing']['items'],icq["sharing"]['other'])

        ui.html('<h2>'+icq['current_location']['label']+'</h2>',sanitize=False).classes('wide-input')
        your_location=ui.leaflet(center=(icq['current_location']['coordinates']['lat'],icq['current_location']['coordinates']['lng']), zoom=4).classes('wide-input').style('height: 400px; width: 100%;')
        markers=[]
        if icq['current_location']['placed']==True:
            markers.append(your_location.marker(latlng=(icq['current_location']['coordinates']['lat'],icq['current_location']['coordinates']['lng'])))
        def click_on_your_location(e: events.GenericEventArguments):
            lat = e.args['latlng']['lat']
            lng = e.args['latlng']['lng']
            clear()
            markers.append(your_location.marker(latlng=(lat, lng)))
            app.storage.user['user_info']['icq']['current_location']['coordinates']['lat']=lat
            app.storage.user['user_info']['icq']['current_location']['coordinates']['lng']=lng
            icq['current_location']['placed']=True
            print('Location selected: ',app.storage.user['user_info']['icq']['current_location']['coordinates'])
        your_location.on('map-click', click_on_your_location)
        def clear():
            for marker in markers:
                your_location.remove_layer(marker)
            markers.clear()
        with container:
            ui.html('<br><h2>'+icq['potential_locations']['label']+'</h2>',sanitize=False).classes('wide-input')
            pot_loc=ui.editor(placeholder="Your other ideas here...").bind_value(icq['potential_locations'],'value',strict=False).classes('wide-input')
        # print('sub: ',app.storage.user['user_info']['sub'])
    ui.timer(1,partial(save_me,'user_profile:'+str(app.storage.user['user_info']['sub']),icq))
async def privacy_policy():
    ui.label('Privacy Policy Coming Soon!')
def makeRadarIndicator(name, max_value):
    return {"name": name, "max": max_value}
def makeLegendData(data):
    return {
        "name":data,
    }
def makeRadar(data,legend):
    dataObj={
                "name": str(legend),
                "value": data.tolist()
            } 
    return dataObj
def makeRadarSeries(datas,legend):  
    dataObj=list(range(len([datas])))
    for d in range(len([datas])):
        data=[datas][d]
        dataObj[d]={
                "type": "radar",
                "radarIndex": d,
                "data":[makeRadar(data[i],legend[i]) for i,l in enumerate(legend)]
        }
    return dataObj
def point_clicked(e : events.EChartPointClickEventArguments):
    print(e.name,e.data)
    # RedirectResponse('/view_profile/'+)
def radial_chart(data,indicators,legend,title,user):
    """This function shows data as a radar plot
    Args:
        data (list of lists ([[],[]])): the data to be plotted, each number in a sublist corresponds to an indicator
        indicators (_type_): The labels that goes with each number in the sub-list of data
        legend (_type_): The instance of the data that the indicators are referring to
        title (_type_): The title of the plot
    Returns:
        _type_: A NiceGUI radar plot ui element 
    """
    lineStyle = {"width": 1,"opacity": 0.9}
    option = {
        "tooltip": {
            "triggerEvent":True,
            "confine":True,
            "enterable":True,
            "textstyle":{"overflow":"break"}
        },
        "backgroundColor": "#FFF",
        "title": {
            "text": title,
            "left": "center",
            "textStyle": {
                "color": "#333"
            }
        },
        "legend": {
            "triggerEvent":False,
            "bottom":5,
            "data": legend,
            "itemGap": 20,
            "textStyle": {
                "color": "red",
                "fontSize": 14
            },
            "selectedMode": True,
            "coordinateSystem":"radar",
        },
        "radar": {
            "triggerEvent":True,
            "indicator": [makeRadarIndicator(name, 100) for name in indicators[0]],
            "shape": "circle",
            "splitNumber": 5,
            "axisName": {
                "color": "rgb(0, 0, 0)"
            },
            "splitArea": {
                "show": True
            },
            "axisLine": {
                "lineStyle": {
                    "color": "rgba(238, 197, 102, 0.5)"
                }
            }
        },
        "series": makeRadarSeries(data,legend)
    }
    # ui.label(str(option))
    #ui.navigate.to('/view_profile/104343636735404966972')
                # const selected = e.selected;\
                # console.log("Legend selection changed:", e.name, selected,this);\
                # window.location.href = "/view_profile/'+str(user)+'";}'
    # try:
    #     for u in user:
    #         js_handler = '(e) => { console.log(e);\
    #             const selected = e.selected;\
    #             console.log("Legend selection changed:", e.name, selected,this);\
    #             window.location.href = "/view_profile/'+str(u)+'";}'
    # except Exception as e:
    #     print(e)
    #     js_handler = '(e) => { console.log(e);\
    #         const selected = e.selected;\
    #         console.log("Legend selection changed:", e.name, selected,this);\
    #         window.location.href = "/view_profile/'+str(user)+'";}'
    js_handler = '(e) => { console.log(e);}'
    return ui.echart(option,on_point_click=point_clicked,renderer='svg').on('chart:legendselectchanged', js_handler=js_handler).classes('w-full h-128')
async def prevent_default(e: events.GenericEventArguments):
    e.client.handle_event
    # ev=await e.client.run_javascript('function (params) {console.log(params);\
    #     const selected = params.selected;\
    #         selected[params.name] = true;\
    #         this.setOption({\
    #             legend: { selected }\
    #         });\
    #         console.log("Legend selection changed:", params.name, selected);\
    #         window.location.href = \'#\' + params.name;\
    #     });',timeout=5)
    print(e)
def makeBarSeries(data,name):
    dataObject=list(range(len(name)))
    # print(len(name))
    for d in range(0,len(name)):
        # print(d,data[d])
        dataObj=data[d]
        print(dataObj)
        dataObject[d]={
                "name": str(name[d]),
                'type': 'bar',
                'stack': 'total',
                'label': {
                    'show': True
                },
                'emphasis': {
                    'focus': 'series'
                },
                'data':data[d]
            }
    return dataObject
def bar_chart(data,indicators,name,title,user):
    option= {
        "title": {
            "text": title
        },
        "tooltip": {
            "trigger": "axis",
            "axisPointer": {
                "type": "shadow"
            }
        },
        "grid": {
            "top": 80,
            "bottom": 30
        },
        "xAxis": {
            "type": "value",
            "position": "top",
            "splitLine": {
                "lineStyle": {
                    "type": "dashed"
                }
            },
            "boundaryGap": [0, 0.01]
        },
        "yAxis": {
            "type": "category",
            "data": list(indicators[0])
        },
        "series": makeBarSeries(data,name)
    }
    # print('option: ',option.tolist())
    js_handler = '(e) => { console.log(e);}'
    return ui.echart(option,on_point_click=point_clicked,renderer='svg').on('chart:legendselectchanged', js_handler=js_handler).classes('w-full h-128')
async def search_people():
    """
    This function shows information about people in aggregated form, 
    filters users, and allows them to click on a name and have it open their profile
    """
    ui.page_title('Other Us-People')
    sub=app.storage.user['user_info']['sub']
    with ui.grid(columns=1).classes('w-full'):
        try:
            schema=(TextField("$.user_profile.[*].icq",as_name='userprofile'),NumericField("$.user_profile.[*].id",as_name='id'))
            name_for_index_of_users='idx:nice_user:'
            index=r.ft(name_for_index_of_users)
            # index.dropindex()
            # index.create_index(schema,definition=IndexDefinition(prefix=["user_profile:"], index_type=IndexType.JSON))
        except Exception as ex:
            print('couldn\'t del: ',ex)
            schema=(TextField("$.user_profile.[*].icq",as_name='userprofile'),NumericField("$.user_profile.[*].id",as_name='id'))
            name_for_index_of_users='idx:nice_user:'
            index=r.ft(name_for_index_of_users)
            index.create_index(schema,definition=IndexDefinition(prefix=["user_profile:"], index_type=IndexType.JSON))
        qu=Query("*")
        search=index.search(qu)
        peop_docs=index.search(qu.return_field("$.name.value"))
        num_of_peop=peop_docs.total

        want_docs=index.search(qu.return_field("$.wants.items"))
        sharing_docs=index.search(qu.return_field("$.sharing.items"))
        skills_docs=index.search(qu.return_field("$.skills.items"))

        # print('\n\n',num_of_peop,'\n\n',str(peop_docs)),'\n\n',want_docs
        num_of_wanted_items=len(json_loads(want_docs.docs[0]['$.wants.items']).values())
        wants=np.zeros((num_of_peop,num_of_wanted_items))
        wants_label=np.empty((num_of_peop,num_of_wanted_items),dtype=object)

        num_of_shared_items=len(json_loads(sharing_docs.docs[0]['$.sharing.items']).values())
        shares=np.zeros((num_of_peop,num_of_shared_items))
        shares_label=np.empty((num_of_peop,num_of_shared_items),dtype=object)

        num_of_skilled_items=len(json_loads(skills_docs.docs[0]['$.skills.items']).values())
        skills_have=np.zeros((num_of_peop,num_of_skilled_items))
        skills_want=np.zeros((num_of_peop,num_of_skilled_items))
        skills_label=np.empty((num_of_peop,num_of_skilled_items),dtype=object)
        names=[]
        ids=[]
        # print('\n\nnum_wants:','\n'+str(num_of_peop)+'\n - \n'+str(num_of_items)+'\n\n')#,'\ndocs:',search.docs,'index: ',index.info()
        for d, s in enumerate(search.docs):
            contents=json.loads(s['json'])
            try:
                for i,item in enumerate(contents['wants']['items'].values()):
                    wants_label[d,i]=item['label']
                    wants[d,i]=item['value']
                for i, item in enumerate(contents['sharing']['items'].values()):
                    shares_label[d,i]=item['label']
                    shares[d,i]=item['value']
                for i, item in enumerate(contents['skills']['items'].values()):
                    skills_label[d,i]=item['label']
                    skills_have[d,i]=item['have']
                    skills_want[d,i]=item['want']
                names.append(contents['name']['value'])
                ids.append(contents['id'])
                # print(ids,names)
            except Exception as ex:
                print('skipping this', ex)
        skills=[skills_have,skills_want]
        with ui.row(align_items='top'):
            # print(skills_have,'\n',skills_label,'\n',names)
            ui.html('<span style="font-weight:bold">Profiles➡️</span> ',sanitize=False)
            [ui.link(name+' | ','/view_profile/'+str(ids[i])) for i,name in enumerate(names)]
            radial_chart(wants,wants_label,names,'What Social Qualities Do You Desire?',ids)
            radial_chart(shares,shares_label,names,'How Comfortable Are You With Sharing:',ids)
            radial_chart(skills_have,skills_label,names,"What skills do you currently have?",ids)
            radial_chart(skills_want,skills_label,names,"What skills do you currently want to acquire more of?",ids)
        
        # ui.html(str(wants),sanitize=False)
async def test():
    with ui.column(align_items='center'):
        ui.add_body_html("""
            <h1>HELP!</h1>
            <h1>HELP!</h1>
            <h1>HELP!</h1>
            <h1>HELP!</h1>
            <h1>HELP!</h1>
            <h1>HELP!</h1>
            <h1>HELP!</h1>
            <h1>HELP!</h1>
            <h1>HELP!</h1>
            <h1>HELP!</h1>
            <h1>HELP!</h1>
            <script>
                console.log('otherrealmFunctions.js loaded');
                echart.on('legendselectchanged', function (params) {
                    const selected = params.selected;
                    selected[params.name] = true;
                    this.setOption({
                        legend: { selected }
                    });
                    console.log('Legend selection changed:', params.name, selected);
                    window.location.href = '#'+params.name;
                });
            </script>
            """,shared=False)
async def view_profile(id):
    print(id)
    ui.page_title('Other Us-Profile')
    user_data=r.json().get('user_profile:'+id+':icq')
    sub=app.storage.user['user_info']['sub']
    with ui.grid(columns=1).classes('w-full'):
        # print(id,user_data)
        ui.html('<h1 class="center-title">'+user_data['name']['value']+'</h1>',sanitize=False).classes('wide-input')
        if user_data['profile_image']['src']!='':
            ui.image('data:image/png;base64,'+user_data['profile_image']['src']).style('max-width:400px;width:100%').classes('wide-input')
        ui.html('<h2>Social Media/Other Links:</h2>',sanitize=False).classes('wide-input')
        with ui.column(wrap=True, align_items='center').classes('wide-input'):
            for url in user_data['urls']['value']:
                ui.link(url,url).classes('wide-input')
        ui.html('<h2>Transhumanist Ideas:</h2>',sanitize=False).classes('wide-input')
        ui.markdown(user_data['transhumanist_ideas']['value']).classes('wide-input')
        ui.html('<h2>Other Crazy Ideas:</h2>',sanitize=False).classes('wide-input')
        ui.markdown(user_data['crazy_ideas']['value']).classes('wide-input')
        if str(user_data['video_series']['value'])=='Yes' or str(user_data['video_series']['value'])=='No' or str(user_data['video_series']['value'])=='Maybe':
            ui.html('<h2>Interested in Video Series?</h2>',sanitize=False).classes('wide-input')
            ui.label(user_data['video_series']['value']).classes('wide-input')
        ui.html('<h2>'+user_data['wants']['label']+'</h2>',sanitize=False).classes('wide-input')
        # print('\n\n',num_of_peop,'\n\n',str(peop_docs)),'\n\n',want_docs
        num_of_wanted_items=len(user_data['wants']['items'].values())
        wants=np.zeros((num_of_wanted_items))
        wants_label=np.empty((num_of_wanted_items),dtype=object)
        num_of_shared_items=len(user_data['sharing']['items'].values())
        shares=np.zeros((num_of_shared_items))
        shares_label=np.empty((num_of_shared_items),dtype=object)
        num_of_skilled_items=len(user_data['skills']['items'].values())
        skills_have=np.zeros((num_of_skilled_items))
        skills_want=np.zeros((num_of_skilled_items))
        skills_label=np.empty((num_of_skilled_items),dtype=object)
        names=[]
        ids=[]
        try:
            for i,item in enumerate(user_data['wants']['items'].values()):
                wants_label[i]=item['label']
                wants[i]=item['value']
            for i, item in enumerate(user_data['sharing']['items'].values()):
                shares_label[i]=item['label']
                shares[i]=item['value']
            for i, item in enumerate(user_data['skills']['items'].values()):
                skills_label[i]=item['label']
                skills_have[i]=item['have']
                skills_want[i]=item['want']
            names.append(user_data['name']['value'])
            ids.append(user_data['id'])
        except Exception as ex:
            print('skipping this', ex)
        print(wants.tolist(),'859\n',wants.tolist(),'\n',names)
        bar_chart(wants,wants_label,names,'What Social Qualities Do You Desire?',id)
        bar_chart(shares,shares_label,names,'How Comfortable Are You With Sharing:',id)
        bar_chart(skills_have,skills_label,names,"What skills do you currently have?",id)
        bar_chart(skills_want,skills_label,names,"What skills do you currently want to acquire more of?",id)
def error():
    raise ValueError('some error message')
# NOTE: this ensures that you can run the app locally, accessing via http://127.0.0.1:8086 is not supported by Google OAuth2 otherus.theotherrealm.org
ui.run(
    root=main,
    title='Otherus - The Other Realm',
    host='localhost',  # NOTE: this ensures that you can run the app locally, accessing via http://127.0.0.1:8086 is not supported by Google OAuth2
    port=8086,
    storage_secret=os.getenv('random_secret'),
    show=False,
    fastapi_docs=True,
    favicon='img/About.png',
    uvicorn_reload_excludes="./.history/*.py"
)