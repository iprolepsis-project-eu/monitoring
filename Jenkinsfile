pipeline {
    agent any
    // note that running this will also run
    // 'rm -rf '/home/jenkins/iProlepsisMonitoring''
    // "rm -rf "tmp/.git"
    // so be sure to verify that there's nothing important there before running this jenkinsfile
    parameters {
        string(name: 'REMOTE_DIR', defaultValue: '/home/jenkins/iProlepsisMonitoring', description: 'Remote directory for deployment')

    }
    
    environment {
        INVENTORY_FILE = "${WORKSPACE}/playbooks/inventory.ini"
        GIT_REPO = 'https://github.com/iprolepsis-project-eu/monitoring'
        GIT_BRANCH = 'main'
    }
    
    stages {   
        stage('Checkout') {
            steps {
                git branch: env.GIT_BRANCH, url: env.GIT_REPO
            }
        }
        
        stage('Get IP Addresses and Create Inventory') {
            steps {
                script {
                    createInventory()
                }
            }
        }
        
        stage('Run Ansible Playbook') {
            steps {
                script {
                    def runningNodes = getRunningNodesFromInventory()
                    echo "Running Nodes (from inventory): ${runningNodes}"
                    
                    runAnsibleOnNodes(runningNodes)
                }
            }
        }
    }
    
    post {
    always {
        archiveArtifacts artifacts: 'playbooks/inventory.ini', fingerprint: true
        }
    }
}

def createInventory() {
    def nodeIpMap = [:]
    
    writeFile file: env.INVENTORY_FILE, text: "[Monitoring]\n"
    
    jenkins.model.Jenkins.instance.computers.each { computer ->
        def nodeName = computer.name
        
        if (nodeName && nodeName != "master" && computer.online) {
            def ipAddresses = computer.getChannel()?.call(new hudson.model.Computer.ListPossibleNames())
            if (ipAddresses) {
                def lastIP = ipAddresses.last()
                nodeIpMap[nodeName] = lastIP
                echo "Node: ${nodeName}, Last IP: ${lastIP}"
                sh "echo '${lastIP} ansible_host=${nodeName}' >> ${env.INVENTORY_FILE}"
            } else {
                echo "No IP addresses found for node: ${nodeName}"
            }
        }
    }
    
    echo "Discovered Running Nodes: ${nodeIpMap}"
    env.NODE_IP_MAP = nodeIpMap.collect { k, v -> "$k=$v" }.join(',')
}

def getRunningNodesFromInventory() {
    def runningNodes = []
    def inventory = readFile(env.INVENTORY_FILE)
    
    inventory.split('\n').each { line ->
        if (line && !line.startsWith('[')) {
            def (ip, hostPart) = line.tokenize() 
            def hostname = hostPart.split('=')[1]
            runningNodes.add([hostname: hostname, ip: ip])
        }
    }
    
    return runningNodes
}

def runAnsibleOnNodes(runningNodes) {
    runningNodes.each { node ->
        sshagent([node.hostname]) {
            try {
                sh "ssh -o StrictHostKeyChecking=no root@${node.ip} 'rm -rf ${params.REMOTE_DIR}'"
                sh """
                    if [ -d "tmp/.git" ]; then
                        rm -rf "tmp/.git"
                    fi
                    mv ${WORKSPACE}/.git /tmp/.git
                    scp -o StrictHostKeyChecking=no -r ${WORKSPACE} root@${node.ip}:${params.REMOTE_DIR}  
                    mv /tmp/.git ${WORKSPACE}/

                    # Install Ansible on the remote machine
                    ssh -o StrictHostKeyChecking=no root@${node.ip} '
                        if ! command -v ansible-playbook &> /dev/null; then
                            apt update
                            apt install -y software-properties-common
                            apt-add-repository --yes --update ppa:ansible/ansible
                            apt install -y ansible
                        fi
                    '

                    ssh -o StrictHostKeyChecking=no root@${node.ip} 'ansible-playbook ${params.REMOTE_DIR}/playbooks/playbook.yml -i "localhost," -e "server_ip=${node.ip} remote_dir=${params.REMOTE_DIR}" -vvv'
                """
            } catch (Exception e) {
                echo "Error occurred while processing node ${node.hostname}: ${e.message}"
                // Optionally, you can throw the error to fail the build
                // throw e
            }
        }
    }
}
