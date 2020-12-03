mkdir -p ~/.streamlit/
echo "\
[general]\n\
email = \"tomcreer@gmail.com\"\n\
[server]\n\
headless = true\n\
enableCORS=false\n\
port = $PORT\n\
" > ~/.streamlit/credentials.toml