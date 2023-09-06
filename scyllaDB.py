from __future__ import print_function
import argparse
import boto3
import sys
import os

parser = argparse.ArgumentParser()
parser.add_argument('--operation', type=str, required=True)
parser.add_argument('--endpoint_url', type=str)
args = parser.parse_args()
def create():
    table = dynamodb.create_table(
        BillingMode='PAY_PER_REQUEST',
        TableName='mutant_data',
        KeySchema=[
        {
            'AttributeName': 'last_name',
            'KeyType': 'HASH'
        },
        ],
        AttributeDefinitions=[
        {
            'AttributeName': 'last_name',
            'AttributeType': 'S'
        },
        ]
    )

    print("Finished creating table ", table.table_name ,". Status: ", table.table_status)

def write():
    

    dynamodb.batch_write_item(RequestItems={
        'mutant_data': [
            {
                'PutRequest': {
                    'Item': {
                        "last_name": "Loblaw",
                        "first_name": "Bob",
                        "address": "1313 Mockingbird Lane"
                    }
                }
            },
            {
                'PutRequest': {
                    'Item': {
                        "last_name": "Jeffries",
                        "first_name": "Jim",
                        "address": "1211 Hollywood Lane"
                    }
                }
            }
        ]
    })

    table = dynamodb.Table('mutant_data')
    print("Finished writing to table ", table.table_name)

def read():
    

    response = dynamodb.batch_get_item(
        RequestItems={
            'mutant_data' : { 'Keys': [{ 'last_name': 'Loblaw' }, {'last_name': 'Jeffries'}] }
        }
    )
    for x in response:
        print (x)
        for y in response[x]:
            print (y,':',response[x][y])
    

if __name__ == "__main__":
    if args.endpoint_url:
        print(args.endpoint_url)
        dynamodb = boto3.resource('dynamodb',endpoint_url= args.endpoint_url)

        if args.operation == 'create':
            create()
        elif args.operation == 'write':
            write()
        elif args.operation == 'read':
            read()
        else:
            print("Invalid argument")

    else:
        dynamodb = boto3.resource('dynamodb') 
        if args.operation == 'create':
            create()
        elif args.operation == 'write':
            write()
        elif args.operation == 'read':
            read()
        else:
            print("Invalid argument")
