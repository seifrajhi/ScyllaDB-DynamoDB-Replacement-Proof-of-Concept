# Proof-of-Concept with ScyllaDB

## What has to be developed?

- Terraform code to deploy a cluster of ScyllaDB with DynamoDB-compatible API endpoint
- test code with boto3 to write and read some records against a DynamoDB table

Credit:
- https://www.scylladb.com/open-source-nosql-database/#dynamodb-compatibleapi

## Automating Scylla deployments with EKS

This example demonstrates a simple example of deploying a Scylla cluster on AWS ELASTIC KUBERNETES SERICE EKS  and Alternator which is an open-source project that gives ScyllaDB compatibility with Amazon DynamoDB.

### Overview
A typical way to organize replicated containers is through Services, which automatically load-balance all instances behind a single IP address.

However, in a stateful application like Scylla with its own cluster management at the application level, treating all instances as interchangable is not suitable.

A StatefulSet  is similar to a Service, but designates persistent names like scylla-0, scylla-1, ..., scylla-n which get dynamically bound to particular Pods.

We still use a "headless" Service (without a single IP address) for aggregating all the running Pods.

### Determining when an instance is ready

Kubernetes queries running instances to determine when they're ready. A simple shell script, ready-probe.sh, uses nodetool to check the status of the node and reports success once it has joined the Scylla cluster.

We use a ConfigMap to describe the ready-probe.sh file, and mount the file at /opt/ready-probe.sh in the StatefulSet description.

### Storage and PersistentVolumes

A StatefulSet also describes a template for a PersistentVolumeClaim for each Pod. PersistentVolumes are dynamically created based on the number of instances in the StatefulSet using the Google Compute Engine storage provisioner.

After a PersistentVolume has been created, it can be dynamically bound to different Pods as the need arises.


## Seeding the cluster

A "seed" list in Scylla's configuration instructs new nodes on which nodes to contact in order to join the Scylla cluster. While the IP address of particular pods is ephemeral, the static identifiers created by the StatefulSet also get mapped to DNS records. We can specify the seed node using these host names. An example is scylla-0.scylla.default.svc.cluster.local

## Demo

This example uses Scylla 5.0.0. we  assumes that the Kubernetes management tools (eksctl, kubectl, awsV2, etc) have been installed locally. We use AWS with Kubernetes.

### Set up and initialize terraform workspace
In your terminal, clone the following repository. It contains the example configuration used in this tutorial.

```powershell
git clone https://github.com/reply-fr/scylladb-proof-of-concept.git
```

Then change into the repository directory.
```powershell
cd eks-scylladb/terraform-eks
```
Initialize your configuration.
```powershell
terraform init
```

### Provision the EKS cluster
Run terraform apply to create your cluster and other necessary resources. Confirm the operation with a yes.
This process should take approximately 10 minutes. Upon completion, Terraform will print your configuration's outputs.
```powershell
terraform apply
```
### Configure kubectl
Now that you've provisioned your EKS cluster, you need to configure kubectl.
First, open the outputs.tf file to review the output values. You will use the region and cluster_name outputs to configure kubectl.
```powershell
aws eks --region $(terraform output -raw region) update-kubeconfig  --name $(terraform output -raw cluster_name)
```

### Verify the Cluster
Use kubectl commands to verify your cluster configuration.

```powershell
kubectl cluster-info
```

### ScyllaDB deployment on EKS

 create the StorageClass instructing Kubernetes on the kind of volumes to create (SSD):
 ```powershell
 kubectl create -f scylla-storageclass.yaml
```

Next, create the Service aggregating Scylla Pods:
```powershell
kubectl create -f scylla-service.yaml
```

Then, create the ConfigMap, for the readiness-checking file:
```powershell
kubectl create -f scylla-configmap.yaml
```

Finally, we're ready to instantiate our Scylla cluster with three nodes:
```powershell
kubectl create -f scylla-statefulset.yaml
```

We can query the resources we've created with commands like kubectl get statefulsets or kubectl describe storageclass scylla.


### Running the Example Application
The application connects to the Scylla cluster, creates a table, inserts two rows into the created table and reads those two rows from the database thanks to the below script.
PS: 
-Change the value for “endpoint_url” to the IP address or DNS hosntname of the cluster.
To run it there are three operations : create, write and read, apply them one by one in the same order.
```powershell
python scyllaDB.py --operation create --endpoint_url "endpoint_url"
```