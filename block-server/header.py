import os
import datetime
import socket
#from TCP_STATUSES import TCP_STATUSES

def set_header_req(metadata, method, path=False, host=False):
  header_fields = {
    'path': path, 
    'Host': host if host else socket.gethostname(),
    'protocol': 'TCP',
    'Content-Length': os.path.getsize(path), # size in byte
    'Content-Type': os.path.splitext(path)[1][1:], # file extenstion
    'Content-Disposition': 'attachment;',
    'filename': os.path.basename(path),
    'Date': str(datetime.datetime.now()) ,
    'Server': 'some_Server',
    'User-Agent': 'Python Shell User Agent 1.0'  # TODO: replace in the browser
  }
  HEADER = method + ' ' + header_fields['Host']  + ' TCP\n'
  for i in header_fields:
    h, v = str(i), str(header_fields[i])
    HEADER += '{0}: {1}{2}'.format(h, v, ' ' if v[len(v)-1] == ';' else '\n')
  return HEADER

def set_header_res(): None
