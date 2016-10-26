# coding=utf-8

from os.path import exists as lexists
import os, time
from fabric.api import env, run, cd, sudo, task, lcd, local, execute, put, roles
from fabric.contrib.files import exists as rexists, contains


def recur_sync(file, remote_dir, count=3, mode=None, use_sudo=False):
    """
    递归性同步文件，如果文件不存在就向父目录查找同名文件
    """
    if(lexists(file)):
        put(file, remote_dir, mode=mode, use_sudo=use_sudo);
        return;
    elif(count> 0):
        arr = os.path.split(file);
        path = os.path.abspath(arr[0] + '/..')
        recur_sync(path + '/' + arr[1], remote_dir, count-1, mode=mode, use_sudo=use_sudo);


class SpringBootServer(object):
    """
    Tomcat server
    """
    def __init__(self, project_name, project_home, project_owner, env):
        self.projectName = project_name;
        self.projectHome = project_home;
        self.projectOwner = project_owner;
        self.env = env;
        self.remoteProjectBaseDir = '/data/project/';
        self.remoteConfigBaseDir = '/data/config/';
        self.remoteLogBaseDir = '/data/logs/tomcat/';
        self.remoteLogDir = self.remoteLogBaseDir + self.projectName + '/';
        self.remoteProjectDir = self.remoteProjectBaseDir + self.projectName + '/';
        self.remoteProjectDirBak = self.remoteProjectBaseDir + self.projectName + '_bak/';
        self.remoteConfigDir = self.remoteConfigBaseDir + self.projectName + '/';
        self.remoteConfigDirBak = self.remoteConfigBaseDir + self.projectName + '_bak/';
        self.remoteSprintBootShell = self.remoteProjectDir + 'spring-boot.sh';

    def checkRemote(self):
        """
        check remote server
        """
        if not contains('/etc/passwd', self.projectOwner, use_sudo=True):
            sudo('useradd -m -s "/bin/bash" %s' % (self.projectOwner));
        self.checkRemoteDir(self.remoteLogDir, self.projectOwner);
        self.checkRemoteDir(self.remoteProjectDir, self.projectOwner);
        self.checkRemoteDir(self.remoteConfigDir, self.projectOwner);

    def syncCode(self):
        """
        get latest source codes and deploy to remote host
        """
        if(not lexists(self.projectHome + 'target/' + self.projectName + '.jar')):
            raise Exception("classes or lib folder is not exist.");
        with lcd(self.projectHome):
            put('target/' + self.projectName + '.jar', self.remoteProjectDir, use_sudo=True);
        recur_sync(self.env + '/env.sh', self.remoteProjectDir, 2, mode=0400, use_sudo=True);
        recur_sync('../spring-boot.sh', self.remoteProjectDir, mode=0777, use_sudo=True);
        put(self.env + '/application.properties', self.remoteConfigDir, mode=0400, use_sudo=True);
        put(self.env + '/logback.xml', self.remoteConfigDir, mode=0400, use_sudo=True);
        sudo(('chown -R %s:%s %s; chown -R %s:%s %s' % (self.projectOwner, self.projectOwner, self.remoteProjectDir, self.projectOwner, self.projectOwner, self.remoteConfigDir)));

    def backup(self):
        """
        backup source folders.
        """
        if(rexists(self.remoteProjectDir)):
            sudo('rm -rf ' + self.remoteProjectDirBak);
            sudo("mv -f %s %s" % (self.remoteProjectDir, self.remoteProjectDirBak));
            sudo(('mkdir -pv %s; chown -R %s:%s %s' % (self.remoteProjectDir, self.projectOwner, self.projectOwner, self.remoteProjectDir)));
        if(rexists(self.remoteConfigDir)):
            sudo('rm -rf ' + self.remoteConfigDirBak);
            sudo("mv -f %s %s" % (self.remoteConfigDir, self.remoteConfigDirBak));
            sudo(('mkdir -pv %s; chown -R %s:%s %s' % (self.remoteConfigDir, self.projectOwner, self.projectOwner, self.remoteConfigDir)));

    def stop(self):
        if(rexists(self.remoteSprintBootShell)):
            sudo('%s stop' % (self.remoteSprintBootShell));


    def start(self):
        sudo(self.remoteSprintBootShell + ' start');
        time.sleep(3);

    def deploy(self):
        """
        deploy the project to servers
        """
        execute(self.checkRemote);
        execute(self.stop);
        execute(self.backup);
        execute(self.syncCode);
        execute(self.start);

    def rollback(self):
        """
        rollback the project in servers
        """
        if(not rexists(self.remoteProjectDir)):
            raise Exception(("The project folder(%s) is not exist in host %s." % (self.remoteProjectDir, env.host)));
        if(rexists(self.remoteProjectDirBak) and rexists(self.remoteConfigDirBak)):
            execute(self.stop);
            sudo('rm -rf ' + self.remoteProjectDir);
            sudo("mv -f %s %s" % (self.remoteProjectDirBak, self.remoteProjectDir));
            sudo('rm -rf ' + self.remoteConfigDir)
            sudo("mv -f %s %s" % (self.remoteConfigDirBak, self.remoteConfigDir));
            execute(self.start);
        else:
            raise Exception(("The backup folder(%s or %s) is not exist in host %s." % (self.remoteProjectDirBak, self.remoteConfigDirBak, env.host)));

    def checkRemoteDir(self, dir, owner):
        """
        check remote folder.
        if not, create it
        """
        if(not rexists(dir)):
            sudo(('mkdir -pv %s;chown -R %s:%s %s' % (dir, owner, owner, dir)))
