#!/bin/bash
eksctl create cluster \
--name $1 \
--region $2 \
--nodegroup-name worknodes-1 \
--node-type t3.medium \
--nodes 2 \
--nodes-min 1 \
--nodes-max 4 \
--managed