#!/bin/bash
CWD=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd ${CWD}

# environment
set -a
source devops/commons.env
source devops/secrets.env

function ec2SSH() {
    chmod 400 $EC2_KEYPAIR
    ssh -i $EC2_KEYPAIR $EC2_HOST
}

function awsConfigure() {
    aws configure --profile ${ADMIN_AWS_PROFILE} set aws_access_key_id ${ADMIN_ACCESS_KEY_ID}
    aws configure --profile ${ADMIN_AWS_PROFILE} set aws_secret_access_key ${ADMIN_SECRET_ACCESS_KEY}
    aws configure --profile ${ADMIN_AWS_PROFILE} set region ${ADMIN_BACKUP_AWS_REGION}
}

function privateDockerLogin() {
    awsConfigure
    # private docker login
    echo $(aws ecr get-login --profile ${ADMIN_AWS_PROFILE} | cut -d' ' -f6) | docker login -u AWS --password-stdin https://${PRIVATE_DOCKER_REGISTRY}
}


function upService() {
    # INPUT VARIABLE
    export DEPLOY_ENV=${2}

    ENVS=(local prod)
    [[ ! " ${ENVS[@]} " =~ " ${DEPLOY_ENV} " ]] && echo "PLEASE USE ENV: ${ENVS[@]}" && exit 0

    docker-compose -f devops/docker-compose.yml down

    case "${DEPLOY_ENV}" in
    local)
        
        docker-compose -f devops/docker-compose.yml up -d
        ;;
    prod)
        docker-compose -f devops/docker-compose.yml up -d
        ;;
    esac

}


COMMAND=$1

case $COMMAND in

    upload)
        docker exec -w /scripts -i ${SERVICE_NAME}-mongodb sh -c "bash db-scripts.sh exportAndUpload"
        ;;

    ec2-login)
        ec2SSH
        ;;

    ec2-deploy)
        ec2Deploy
        ;;

    up)
        upService $@
        ;;
    
    build)
        docker-compose -f devops/docker-compose.yml build
        ;;

    down)
        docker-compose -f devops/docker-compose.yml down
        ;;

    exec)
        docker-compose -f devops/docker-compose.yml exec ${2} bash
        [ $? -ne 0 ] && echo -e "\nPLEASE USE:\n"$(docker-compose -f devops/docker-compose.yml ps --services) "\n" && exit 0
        ;;

    log)
        docker-compose -f devops/docker-compose.yml logs -f ${2}
        [ $? -ne 0 ] && echo -e "\nPLEASE USE:\n"$(docker-compose -f devops/docker-compose.yml ps --services) "\n" && exit 0
        ;;

    run)
        python3 server/manage.py
        ;;

esac
