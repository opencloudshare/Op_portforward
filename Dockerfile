FROM centos:7
EXPOSE 39696
RUN yum install -y epel-release
RUN yum install -y python-pip
RUN mkdir -p /root/.pip/
COPY pip.conf /root/.pip/
RUN pip install tornado==4.4.1 ConfigParser
CMD python portforward.py