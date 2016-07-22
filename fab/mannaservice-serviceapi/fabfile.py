#coding=utf-8

"""
auto deploying java web application for orderservice-serviceapi
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
    'live': ['deploy@114.215.128.165','deploy@115.28.40.95'],
    'liveHangzhou':['deploy@172.16.94.9','deploy@172.16.94.24'],
}

project_name = 'orderservice-serviceapi';
project_owner = 'orderservice-serviceapi';
project_home = '/home/git51/fenqifu-orderservice/orderservice-serviceapi/';

qa = SpringBootServer(project_name, project_home, project_owner, 'qa');
live = SpringBootServer(project_name, project_home, project_owner, 'live');
liveHangzhou = SpringBootServer(project_name, project_home, project_owner, 'liveHangzhou');

@task
@roles('live')
def deploy_live():
    live.deploy();

@task
@roles('live')
def rollback_live():
    live.rollback();
    
@task
@roles('liveHangzhou')
def deploy_liveHangzhou():
    liveHangzhou.deploy();

@task
@roles('liveHangzhou')
def rollback_liveHangzhou():
    liveHangzhou.rollback();

@task
@roles('qa')
def deploy_qa():
    qa.deploy();
