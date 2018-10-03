repoDir="/home/orange/repo/src/"
from firebase import firebase
import sys
import os
import json
sys.path.insert(0, repoDir)
from wrappers.logger import loggerFetch
def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='These scripts will initialize the Database for the district and populate relevant details')
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-limit', '--limit', help='Limit on the number of results', required=False)
  parser.add_argument('-s', '--stateCode', help='State for which the delayed payment report needs to be crawld', required=False)
  parser.add_argument('-pc', '--panchayatCode', help='Panchayat for which the delayed payment report needs to be crawld', required=False)
  parser.add_argument('-b', '--blockCode', help='Block for which the data needs to be updated', required=False)
  parser.add_argument('-j', '--jobcard', help='Jobcard for which date needs to be updated', required=False)
  parser.add_argument('-upt', '--updatePanchayatTable', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-dpt', '--deletePanchayatTable', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-ujt', '--updateJobcardTable', help='Update Jobcard Table', required=False, action='store_const', const=1)
  parser.add_argument('-utt', '--updateTransactionTable', help='Update Transaction Table', required=False, action='store_const', const=1)
  parser.add_argument('-djt', '--deleteJobcardTable', help='Update Jobcard Table', required=False, action='store_const', const=1)
  parser.add_argument('-gpt', '--getPanchayatTable', help='Get Panchayat Table', required=False, action='store_const', const=1)
  parser.add_argument('-p', '--populate', help='Get Panchayat Table', required=False, action='store_const', const=1)
  parser.add_argument('-w', '--write', help='Get Panchayat Table', required=False, action='store_const', const=1)

  args = vars(parser.parse_args())
  return args

def main():
  from firebase import firebase
  firebase = firebase.FirebaseApplication('https://libtech-app.firebaseio.com/', None)
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))
  if args['write']:
    d={}
    d=[]
    d.append({'make':'nd','model':'readyToEat','price':95})
    d.append({'make':'sahaja','model':'vegetable','price':55})
    d.append({'make':'tvs','model':'fruit','price':195})
    with open('first.json', 'w') as outfile:  
      json.dump(d, outfile)

  if args['populate']:
    jsonName="districts.json"
    json_data=open(jsonName,encoding='utf-8-sig').read()
    d = json.loads(json_data)
    myDict={}
    for key,values in d.items():
      code=key
      name=values['name']
      parentCode=values['stateCode']
      logger.info(key)
      dictKey="%s_%s_%s" % (code,name,parentCode)
      myDict[dictKey] = {'name': name, 'code': code, 'parentCode': parentCode, 'slug': dictKey }
    logger.info(dictKey)
    result = firebase.patch('https://libtech-app.firebaseio.com/medicines/', myDict)

      
  logger.info("...END PROCESSING") 
  exit(0)

if __name__ == '__main__':
  main()
