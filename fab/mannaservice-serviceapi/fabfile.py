#coding=utf-8

"""
auto deploying java web application for mannaservice-serviceapi
command examples:
fab deploy_live
fab rollback_beta
run 'fab -l' for more
"""

import sys
sys.path.append('..')

from fabric.api import env, task, roles
from web import SpringBootServer

env.roledefs = {
    'qa': ['root@101.200.121.176'],
    'live': ['root@101.200.121.176'],
   
}

project_name = 'mannaservice-serviceapi';
project_owner = 'mannaservice-serviceapi';
project_home = '/home/github/weishengming-manna/mannaservice-serviceapi/';

qa = SpringBootServer(project_name, project_home, project_owner, 'qa');
live = SpringBootServer(project_name, project_home, project_owner, 'live');

@task
@roles('live')
def deploy_live():
    live.deploy();

@task
@roles('live')
def rollback_live():
    live.rollback();


@task
@roles('qa')
def deploy_qa():
    qa.deploy();
