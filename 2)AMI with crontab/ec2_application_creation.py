import boto3
from botocore.exceptions import ClientError



ec2_resource = boto3.resource('ec2',region_name = "ap-southeast-1")
ec2_client = boto3.client('ec2',region_name = "ap-southeast-1")





def vpc_id_gen(group_name):
    ec2 = boto3.client('ec2')
    vpc_response = ec2.describe_vpcs()
    vpc_id = vpc_response.get('Vpcs', [{}])[0].get('VpcId','')

    try:
        response = ec2.create_security_group(GroupName = group_name,
                                            Description = 'Made by boto3',
                                            VpcId = vpc_id)

        security_group_id = response['GroupId']
        print('Security Group Created %s in vpc %s.' % (security_group_id, vpc_id))


        data = ec2.authorize_security_group_ingress(
            GroupId = security_group_id,
            IpPermissions = [
                {'IpProtocol' : 'tcp',
                'FromPort' : 80,
                'ToPort': 80,
                'IpRanges' : [{'CidrIp': '0.0.0.0/0'}]},
                {'IpProtocol' : 'tcp',
                'FromPort' : 22,
                'ToPort': 22,
                'IpRanges' : [{'CidrIp': '0.0.0.0/0'}]}
            ])
        print('Ingress Successfully Set % s' % data)

    except ClientError as e :
        print(e)

    return security_group_id



#메인으로 생성 기존에 있는 AMI 기준으로 만듬
def key_gen(key_name):
    outfile = open('{0}.pem'.format(key_name),'w')
    key_pair = ec2.create_key_pair(KeyName = key_name)
    KeyPairOut = str(key_pair.key_material)
    outfile.write(KeyPairOut)

def ec2_creation(ami_name, security_group_id, tag):
    instances = ec2_resource.create_instances(
    NetworkInterfaces = [{'SubnetId' :'subnet-6ad5de0d',
                        'DeviceIndex':0,
                        'Groups':[security_group_id],
                        }],
    ImageId=ami_name,
    MinCount=1,
    MaxCount=1,
    KeyName="ngnix_key",
    InstanceType="t2.micro",
    TagSpecifications=[
        {
            'ResourceType' : 'instance',
            'Tags': [
                {
                    'Key' : 'ngnix_web',
                    'Value': tag
                },
            ]
        },
    ]
    )

    for instance in instances:
        print(instance.id, instance.instance_type, instance.tags)


def main_genartor():
    # For security need to separate key from remain keys
    # Separate Group from others for convenient

    ami_name={'main' : 'ami-00a807bf2c1f70cdf',
            'application' : 'ami-01f218e1d29d48f87'}

    vpc_id = vpc_id_gen("ngnix_test")
    
    key_gen("ngnix_key")

    main = 'main'
    application = "application"

    #main_gen
    ec2_creation(ami_name[main], vpc_id, main)
    print("main gen")
    # application_gen
    ec2_creation(ami_name[application],vpc_id, application)
    print("application gen")

if __name__ == '__main__':
    main_genartor()
