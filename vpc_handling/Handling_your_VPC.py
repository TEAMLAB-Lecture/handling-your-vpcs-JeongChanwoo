import boto3
import time
import os
from botocore.exceptions import ClientError


def time_generation():
    time_gen = time.strftime('%c', time.localtime(time.time()))
    time_gen = time_gen.replace("  ", " ")
    time_gen = time_gen.replace(" ","_")
    time_gen = time_gen.replace(":","_")

    return time_gen

def create_vpc():
    ec2 = boto3.client('ec2')
    response = ec2.describe_vpcs()
    vpc_id = response.get('Vpcs', [{}])[0].get('VpcId','')

    f_temp = open("./log/vpcs_boto_log.csv", 'r',encoding='utf-8')
    header = f_temp.readline()
    f_temp.close()
    f = open("./log/vpcs_boto_log.csv", 'a+',encoding='utf-8')


    if not header:
        f.write("vpc_id, date, operation\n")


    elif header==("vpc_id, date, operation\n"):
        pass




    g_temp = open("./log/vpcs_boto_error_log.csv", 'r', encoding='utf-8')
    header_error = g_temp.readline()
    g_temp.close()
    g = open("./log/vpcs_boto_error_log.csv", 'a+', encoding='utf-8')

    if not header_error:
        g.write("error, date, operation\n")

    elif header_error==("error, date, operation\n"):
        pass


    group_id_list=[]

    try:
        for ind in range(10):
            print('VPCs_%s' % ind)
            time.sleep(5)
            response = ec2.create_security_group(GroupName = 'HelloBOTO_%s' % ind ,
                                            Description = 'Made by boto3',
                                            VpcId = vpc_id)

            group_id_list.append('HelloBOTO_%s' % ind)
            security_group_id = response['GroupId']

            print('Security Group Created %s in vpc %s.' % (security_group_id, vpc_id))


            data = ec2.authorize_security_group_ingress(
                GroupId = security_group_id,
                IpPermissions = [
                    {'IpProtocol' : 'tcp',
                    'FromPort' : 80 + ind,
                    'ToPort': 80 + ind,
                    'IpRanges' : [{'CidrIp': '0.0.0.0/0'}]},
                    {'IpProtocol' : 'tcp',
                    'FromPort' : 22 + ind,
                    'ToPort': 22 + ind,
                    'IpRanges' : [{'CidrIp': '0.0.0.0/0'}]}
                ])

            vpcs_date = data["ResponseMetadata"]["HTTPHeaders"]["date"]
            group_date = vpcs_date.split(', ')[1]

            #log 생성
            f.write(("%s,%s,%s\n" % (security_group_id, group_date, "Gen" )))

            print('Ingress Successfully Set % s' % data)
        f.close()
    except ClientError as e :
        print(e)
        itme_gen = time_generation()
        g.write(("%s,%s,%s\n" % (e, time_gen, "Gen" )))
        g.close()

    # return group_id_list


def delet_vpc():
    # Create EC2 Client
    ec2 = boto3.client('ec2')



    # Delet security Group
    f = open("./log/vpcs_boto_log.csv", 'a+',encoding='utf-8')

    g = open("./log/vpcs_boto_error_log.csv", 'a+',encoding='utf-8')

    vpc_group_id = []

    try:
        result = ec2.describe_security_groups()
        for value in result["SecurityGroups"]:
            group_id = value["GroupId"]
            group_name = value["GroupName"]
            print(group_id)
            vpc_group_id.append(group_id)



            response = ec2.delete_security_group(GroupId = group_id)
            time_gen = time_generation()
            print('Security Group Deleted_%s' % (group_name))

            f.write(("%s,%s,%s\n" % (group_id, time_gen, "Del" )))

        f.close()



    except ClientError as e:
        print(e)
        time_gen = time_generation()
        g.write(("%s,%s,%s\n" % (e, time_gen, "Del" )))
        g.close()


def s3_insert(bucket_name):
    s3 = boto3.client('s3')
    response = s3.list_buckets()



    bucket_name = bucket_name
    bucekts = [bucket['Name'] for bucket in response['Buckets']]

    def file_down(bucket_name,file_name):
        try:
            resource.Bucket(bucket_name).download_file(file_name,'./log/%s_copy.csv' % file_name)
        except ClientError as e:
            if e.response['Error']['Code'] == "404":
                print("The object does not exist.")

            else:
                raise


    if bucket_name not in bucekts:
        s3 = boto3.client('s3', region_name = "ap-southeast-1")
        response = s3.create_bucket(
            Bucket = bucket_name,
            CreateBucketConfiguration ={
                'LocationConstraint' : 'ap-southeast-1'
            }
        )
    else:
        pass

    resource = boto3.resource('s3')
    bucket = resource.Bucket(bucket_name)
    bucket_file_list = bucket.objects.all()
    print(bucket_file_list)
    local_file_list = os.listdir("./log/")

    for local_file_name in local_file_list:
        if local_file_name in bucket_file_list:
            file_down(bucket_name, local_file_name)
            f_copy = open("./log/%s_copy.csv" % local_file_name, 'a+',encoding='utf-8')
            f = open("./log/%s.csv" % local_file_name, 'r',encoding='utf-8')

            lines = f.readlines[1:] #헤드 제거
            for line in lines:
                f_copy.write(line)
            f.close()
            f_copy.close()
            s3.upload_file("./log/%s_copy.csv" % local_file_name, bucket_name, local_file_name)
            os.remove('./log/%s_copy.csv' % local_file_name)




        else:
            s3.upload_file("./log/%s" % local_file_name, bucket_name, local_file_name)

if __name__ == '__main__':
    # create_vpc()
    delet_vpc()
    bucket_name = 'gachon-big-data-test'
    s3_insert(bucket_name)
