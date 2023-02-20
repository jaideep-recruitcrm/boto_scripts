#!/bin/bash

shopt -s expand_aliases

source ~/.bash_aliases

aws sts get-session-token --duration-seconds 900 > token.txt
