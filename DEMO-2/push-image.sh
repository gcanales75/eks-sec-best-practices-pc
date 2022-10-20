#!/bin/bash

export ecrRepo=demo-eks-partnercast
export image=docker/getting-started
export ACCOUNT_NUMBER=`aws sts get-caller-identity --query 'Account' --output text`
export AWS_DEFAULT_REGION=us-west-2
export tag=`date +%s`

aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin $ACCOUNT_NUMBER.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com
docker pull $image
docker tag $image:latest $ACCOUNT_NUMBER.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$ecrRepo:$tag
docker push $ACCOUNT_NUMBER.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$ecrRepo:$tag