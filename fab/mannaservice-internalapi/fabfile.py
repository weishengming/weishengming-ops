#coding=utf-8

"""
auto deploying java web application for mannaservice-internalapi
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
    'qa': ['deploy@10.1.0.48'],
    'live': ['deploy@101.200.121.176'],
}

project_name = 'mannaservice-internalapi';
project_owner = 'mannaservice-internalapi';
project_home = '/home/github/weishengming-mannaservice/mannaservice-internalapi/';

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
