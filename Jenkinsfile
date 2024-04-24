pipeline {
  agent any

  stages {
    stage('Copy to DigitalOcean machine') {
            steps {
                // Copy the repository files to the DigitalOcean machine
                sshagent(['DigitalOceanSSHKey']) {
                    sh 'scp -r * root@209.97.183.9:/home/iprolepsis/monitoring'
                }
            }
        }

        stage('Execute docker-compose command') {
            steps {
                // Execute the docker-compose command on the DigitalOcean machine
                sshagent(['DigitalOceanSSHKey']) {
                    sh 'ssh root@209.97.183.9 "cd /home/iprolepsis/monitoring && docker-compose up -d"'
                }
            }
        }
    }
}
