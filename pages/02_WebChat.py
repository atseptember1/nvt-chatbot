import os
import streamlit as st
import streamlit.components.v1 as components

# From here down is all the StreamLit UI.
st.set_page_config(page_title="GPT Smart Agent", page_icon="📖", layout="wide")
# Add custom CSS styles to adjust padding
    
st.markdown("""
        <style>
               .block-container {
                    padding-top: 1rem;
                    padding-bottom: 0rem;
                }
        </style>
        """, unsafe_allow_html=True)


BOT_SERVICE_DIRECT_LINE_SECRET = os.environ.get("BOT_SERVICE_DIRECT_LINE_SECRET")

components.html(
f"""
<html>
  <head>
    <script
      crossorigin="anonymous"
      src="https://cdn.botframework.com/botframework-webchat/latest/webchat.js"
    ></script>
    <script crossorigin="anonymous" src="https://unpkg.com/markdown-it@10.0.0/dist/markdown-it.min.js"></script>
     <style>
      html,
      body {{
          height: 100%;
          background-color: white;
          background-size: cover;
          color: black;
          font-family: 'Segoe UI', Calibri, sans-serif;
      }}

      body {{
        padding-left: 5px;
      }}

      #webchat {{
        height: 85%;
        width: 100%;
      }}

      .webchat__send-box{{
        margin-top: 25px;
        background-color: "black";
        border-style: solid;
        border-width: 1px;
      }}

      
      
    </style>
  </head>
  <body>
    
    <h1><img src='https://noventiq.com/images/svg/noventiq/logo.svg' height="60"></h1> 
    <div id="webchat" role="main"></div>
    <script>
      // Set  the CSS rules.
      const styleSet = window.WebChat.createStyleSet({{
          bubbleBackground: 'transparent',
          bubbleBorderColor: 'darkslategrey',
          bubbleBorderRadius: 5,
          bubbleBorderStyle: 'solid',
          bubbleBorderWidth: 0,
          bubbleTextColor: 'black',

          userAvatarBackgroundColor: 'rgba(53, 55, 64, .3)',
          bubbleFromUserBackground: 'transparent', 
          bubbleFromUserBorderColor: '#E6E6E6',
          bubbleFromUserBorderRadius: 5,
          bubbleFromUserBorderStyle: 'solid',
          bubbleFromUserBorderWidth: 0,
          bubbleFromUserTextColor: 'black',

          notificationText: 'white',

          bubbleMinWidth: 400,
          bubbleMaxWidth: 720,

          botAvatarBackgroundColor: 'white',
          avatarBorderRadius: 40,
          avatarSize: 40,

          rootHeight: '100%',
          rootWidth: '100%',
          backgroundColor: 'rgba(70, 130, 180, .2)',

          hideUploadButton: 'true'
      }});
      // After generated, you can modify the CSS rules.
      // Change font family and weight. 
      styleSet.textContent = {{
          ...styleSet.textContent,
          fontWeight: 'regular'
      }};

      // Set the avatar options. 
      const avatarOptions = {{
          botAvatarInitials: '.',
          userAvatarInitials: 'Me',
          botAvatarImage: 'https://noventiq.com/favicon.ico',
          
          }};
      const markdownIt = window.markdownit({{html:true}});
      window.WebChat.renderWebChat(
        {{
          directLine: window.WebChat.createDirectLine({{
            token: '{BOT_SERVICE_DIRECT_LINE_SECRET}'
          }}),
          renderMarkdown: markdownIt.render.bind(markdownIt),
          styleSet, styleOptions: avatarOptions,
          locale: 'en-US'
        }},
        document.getElementById('webchat')
      );
    </script>
  </body>
</html>
""", height=800)