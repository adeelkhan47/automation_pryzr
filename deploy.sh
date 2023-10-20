#!/usr/bin/sh

red=`tput setaf 1`
whitebg=`tput setab 7`
reset=`tput sgr0`

echo "${red}${whitebg}Updating code...${reset}"
git pull
echo "${red}${whitebg}Stopping app container${reset}"
docker stop autom8_app
docker rm -f autom8_app
docker rmi automation_pryzr_python_app -f
echo "${red}${whitebg}Rebuilding...${reset}"
yes | docker-compose up -d 
echo "${red}${whitebg}Deployment complete.${reset}"
