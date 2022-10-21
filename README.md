# eks-sec-best-practices-pc

**EKS Security best practices - PartnerCast**

### DEMO 1 - GuardDuty Findings

1. Enable GuardDuty (Wait at least 2 hours)

1. Create Lambda

1. Create SNS topic and Suscription (target Lambda)

1. Create EventBridge rule, target SNS topic

1. Create risky pod

1. Wait

### DEMO 2 - Scan images with ECR

1. Create ECR repo with enhaced scanning

1. Create Lambda

1. Create EventBridge rule, target Lambda

1. Run `push-image.sh`

### DEMO 3 - Kubernetes Secrets with AWS Secrets Manager

Reference: https://docs.aws.amazon.com/secretsmanager/latest/userguide/integrating_csi_driver.html
https://docs.aws.amazon.com/secretsmanager/latest/userguide/integrating_csi_driver.html#integrating_csi_driver_install

1. Install the ASCP

  ```
  helm repo add secrets-store-csi-driver https://kubernetes-sigs.github.io/secrets-store-csi-driver/charts
  helm install -n kube-system csi-secrets-store secrets-store-csi-driver/secrets-store-csi-driver

  helm repo add aws-secrets-manager https://aws.github.io/secrets-store-csi-driver-provider-aws
  helm install -n kube-system secrets-provider-aws aws-secrets-manager/secrets-store-csi-driver-provider-aws
  ```

1. Add IAM policy to Cloud9 instance profile

  ```
  SecretsManagerReadWrite
  IAMFullAccess
  ```

1. Add variables

  ```
  REGION=<REGION>
  CLUSTERNAME=<CLUSTERNAME>
  ```

1. Create secret

  ```
  aws --region "$REGION" secretsmanager  create-secret --name MySecret --secret-string '{"username":"gilberto", "password":"canales"}'
  ```

1. Create policy

  ```
  POLICY_ARN=$(aws --region "$REGION" --query Policy.Arn --output text iam create-policy --policy-name secrets-manager-access-policy --policy-document '{
      "Version": "2012-10-17",
      "Statement": [ {
          "Effect": "Allow",
          "Action": ["secretsmanager:GetSecretValue", "secretsmanager:DescribeSecret"],
          "Resource": ["arn:aws:secretsmanager:us-west-2:889653897043:secret:MySecret-IFcoS9"]
      } ]
  }')
  ```

1. Create an IAM OIDC provider

  ```
  eksctl utils associate-iam-oidc-provider --region="$REGION" --cluster="$CLUSTERNAME" --approve
  ``` 

1. Create the service account the pod uses and associate the resource policy you created before

  ```
  eksctl create iamserviceaccount --name secrets-manager-deployment-sa --region="$REGION" --cluster "$CLUSTERNAME" --attach-policy-arn "$POLICY_ARN" --approve --override-existing-serviceaccounts
  ```

1. Install the secret provider

  ```
  kubectl create -f secretProvider.yaml
  ```

1. Create deployment

  ```
  kubectl create -f secret-deploy.yaml
  ```

1. Launch shell in secret pod

  ```
  kubectl exec --stdin --tty nginx-secret-deployment-5d98f9ffc-p2mm7 -- /bin/sh
  ```

1. `cat` into the secret volume

### DEMO 4 - RBAC IAM integration

1. Create user `k8s-dev-user` with no permissions.

1. Create `k8s-dev-role` role with `sts:AssumeRole` privileges. Use `Custom trust policy` if using the UI console. No policy added.

  Trust policy
  ```
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Sid": "Statement1",
        "Effect": "Allow",
        "Principal": {
          "AWS": "arn:aws:iam::<AWS_ACCOUNT_NUMBER>:root"
        },
        "Action": "sts:AssumeRole"
      }
    ]
  }
  ```

1. Add inline policy with `eks:DescribeCluster` to role

1. Create group `k8s-devs`

1. Add inline policy to role to give permisssions to assume role `k8s-dev-role`

  ```
  {
      "Version": "2012-10-17",
      "Statement": [
          {
              "Sid": "VisualEditor0",
              "Effect": "Allow",
              "Action": "sts:AssumeRole",
              "Resource": "arn:aws:iam::<AWS_ACCOUNT_NUMBER>:role/k8s-dev-role"
          }
      ]
  }
  ```

1. Add user `k8s-dev-user` to group `k8s-devs`

1. Create `development` namespace in EKS cluster

1. Create K8s `Role` and `RoleBinding`

1. Update the `aws-auth` ConfigMap to allow our IAM roles, first take a look at the the ConfigMap `kubectl get cm -n kube-system aws-auth -o yaml`

  ```
  export ACCOUNT_ID=$(aws sts get-caller-identity --output text --query Account)
  ```

  ```
  eksctl create iamidentitymapping \
    --cluster eks-cluster-1 \
    --arn arn:aws:iam::${ACCOUNT_ID}:role/k8s-dev-role \
    --username dev-user
  ```

1. Go to a local console to add `k8s-dev-user` profile (Edit: ~/.aws/credentials)

  ```
  aws configure
  ```

  ```
  aws configure set region us-west-2 --profile k8s-dev-user
  ```

1. STS assume role

  ```
  export ACCOUNT_ID=$(aws sts get-caller-identity --profile k8s-dev-user --output text --query Account)
  ```

  ```
  export $(printf "AWS_ACCESS_KEY_ID=%s AWS_SECRET_ACCESS_KEY=%s AWS_SESSION_TOKEN=%s" \
  $(aws sts assume-role \
  --role-arn arn:aws:iam::${ACCOUNT_ID}:role/k8s-dev-role \
  --role-session-name k8s-dev-user-session \
  --profile k8s-dev-user \
  --query "Credentials.[AccessKeyId,SecretAccessKey,SessionToken]" \
  --output text))
  ```

1. Caller identity

  ```
  aws sts get-caller-identity
  ```

1. Update locally `kubeconfig` file (`eks:DescribeCluster` permission required)

  ```
  aws eks --region us-west-2 update-kubeconfig --name eks-cluster-1
  ```

1. Create `nginx` pod

  ```
  kubectl run nginx --image=nginx
  ```

1. kubectl get po & delete -- see errors

1. Edit `dev-role` and add delete permissions

  ```
  kubectl edit role dev-role -n development
  ```

1. Delete `nginx` pod

  ```
  kubectl delete po nginx -n development
  ```
