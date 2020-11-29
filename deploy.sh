#!/bin/bash
CWD=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd ${CWD}

# environment
set -a
source devops/commons.env
source devops/secrets.env

function ec2SSH() {
    export SERVER_NAME=${2}

    case $SERVER_NAME in
        server)
            chmod 400 $EC2_KEYPAIR
            ssh -i $EC2_KEYPAIR $EC2_HOST
            ;;
        scrape)
            chmod 400 $SCRAPE_KEYPAIR
            ssh -i $SCRAPE_KEYPAIR $SCRAPE_HOST
            ;;
    esac
}


function ec2Deploy() {
    export SERVER_NAME=${2}

    case $SERVER_NAME in
        server)
            chmod 400 $EC2_KEYPAIR
            ssh -i $EC2_KEYPAIR $EC2_HOST 'git -C ~/sexy-girls pull && ~/sexy-girls/deploy.sh up prod'
            ;;
        scrape)
            chmod 400 $SCRAPE_KEYPAIR
            ssh -i $SCRAPE_KEYPAIR $SCRAPE_HOST 'git -C ~/sexy-girls pull && ~/sexy-girls/deploy.sh up scrape'
            ;;
    esac
}
function awsConfigure() {
    aws configure --profile ${ADMIN_AWS_PROFILE} set aws_access_key_id ${ADMIN_ACCESS_KEY_ID}
    aws configure --profile ${ADMIN_AWS_PROFILE} set aws_secret_access_key ${ADMIN_SECRET_ACCESS_KEY}
    aws configure --profile ${ADMIN_AWS_PROFILE} set region ${ADMIN_BACKUP_AWS_REGION}
}

function privateDockerLogin() {
    awsConfigure

    echo $(aws ecr get-login --profile ${ADMIN_AWS_PROFILE} | cut -d' ' -f6) | docker login -u AWS --password-stdin https://${PRIVATE_DOCKER_REGISTRY}
}


function upService() {
    export DEPLOY_ENV=${2}

    ENVS=(local prod scrape)
    [[ ! " ${ENVS[@]} " =~ " ${DEPLOY_ENV} " ]] && echo "PLEASE USE ENV: ${ENVS[@]}" && exit 0

    docker-compose -f devops/docker-compose.yml down

    cp server/databases.sqlite3 server/tempDatabases.sqlite3
    mkdir -p server/tempStorages/images

    case "${DEPLOY_ENV}" in
    local)
        docker-compose -f devops/docker-compose.yml up -d nginx server
        ;;
    prod)
        docker-compose -f devops/docker-compose.yml up -d nginx server
        ;;

    scrape)
        docker-compose -f devops/docker-compose.yml up -d scrape
        ;;
    esac

}

function redisCli() {
    export DEPLOY_ENV=${2}

    ENVS=(local prod)
    [[ ! " ${ENVS[@]} " =~ " ${DEPLOY_ENV} " ]] && echo "PLEASE USE ENV: ${ENVS[@]}" && exit 0

    case $DEPLOY_ENV in
        prod)
            REDIS_DB=0
            ;;
        local)
            REDIS_DB=1
            ;;
    esac
}


COMMAND=$1

case $COMMAND in

    upload)
        docker exec -w /scripts -i ${SERVICE_NAME}-mongodb sh -c "bash db-scripts.sh exportAndUpload"
        ;;

    login)
        ec2SSH $@
        ;;

    deploy)
        ec2Deploy $@
        ;;

    up)
        upService $@
        ;;
    
    build)
        awsConfigure
        aws s3 cp --profile $ADMIN_AWS_PROFILE s3://sexy-girls-website/sexy-girls-secrets/ssl-config/$PROD_SERVER_HOST ${CWD}/devops/ssl-config --recursive

        cat ${CWD}/devops/ssl-config/certificate.crt > ${CWD}/devops/ssl-config/certificate-bundle.crt
        echo '' >> ${CWD}/devops/ssl-config/certificate-bundle.crt
        cat ${CWD}/devops/ssl-config/ca_bundle.crt >> ${CWD}/devops/ssl-config/certificate-bundle.crt
        
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
    
    redis-sh)
        redis-cli -h $REDISDB_SERVER -p $REDISDB_PORT -a $REDISDB_PASSWORD
        ;;

    redis-clean)
        redisCli $@

        redis-cli -h $REDISDB_SERVER -p $REDISDB_PORT -a $REDISDB_PASSWORD -n $REDIS_DB FLUSHDB
        
        ;;
esac
