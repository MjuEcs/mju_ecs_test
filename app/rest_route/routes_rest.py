import docker.errors
from flask import Blueprint, render_template, request, jsonify
from app.store import member_memory_store
from app.store import container_memory_store
import docker

server = docker.from_env()

# member_store = member_memory_store.MemberStore()
# container_store = container_memory_store.ContainerStore() 

main = Blueprint('main', __name__)


@main.route('/container', methods=['POST'])
def create_container():
    # {
    #     "container_label": "mycontainer",
    #     "template_id": "ubuntu"
    # }
    try:
        # 요청 데이터 파싱
        data = request.get_json()
        container_label = data.get('container_label')
        template_id = data.get('template_id')

        # 컨테이너 이름 생성 (예: user_id-container_label)
        container_name = container_label  # 실제로는 user_id를 가져와서 user_id + 가져와야함

        # 템플릿 ID에 따라 컨테이너 생성
        if template_id == "ubuntu":
            container = server.containers.run(
                image="ubuntu:22.04",
                name=container_name,
                detach=True,
                mem_limit="2g",
                ports={'22/tcp': 2222},  # 원래는 포트 자동 할당
                hostname=container_name,
                command=['/bin/bash', 'infinity']  # 무한 루프로 컨테이너 유지
            )
        elif template_id == "mysql":
            container = server.containers.run(
                image="mysql:5.7",
                name=container_name,
                detach=True,
                mem_limit="2g", 
                ports={'3306/tcp': 3306},  # 원래는 포트 자동 할당
                environment={
                    "MYSQL_ROOT_PASSWORD": "rootpassword",  # 기본 비밀번호 설정
                    "MYSQL_DATABASE": "mydatabase"
                },
                hostname=container_name
            )
        else:
            return jsonify({
                "status": "error",
                "message": f"Invalid template_id: {template_id}. Supported values are 'ubuntu' and 'mysql'."
            }), 400  # HTTP 상태 코드 400 (Bad Request)

        # 성공 응답 반환
        return jsonify({
            "status": "success",
            "message": f"Container '{container_name}' created successfully.",
            "container_id": container.id,
            "container_name": container.name
        }), 201  # HTTP 상태 코드 201 (Created)

    except docker.errors.APIError as e:
        # Docker API 관련 오류 처리
        return jsonify({
            "status": "error",
            "message": f"Failed to create container: {str(e)}"
        }), 500  # HTTP 상태 코드 500 (Internal Server Error)

    except Exception as e:
        # 기타 예외 처리
        return jsonify({
            "status": "error",
            "message": f"An unexpected error occurred: {str(e)}"
        }), 500  # HTTP 상태 코드 500 (Internal Server Error)

# 컨테이너 삭제
@main.route('/container/<container_name>', methods = ['DELETE'])
def delete_container(container_name):
    try:
        # 컨테이너 검색 및 삭제
        container = server.containers.get(container_name)
        container.remove(force=True)
        
        # 성공 응답 반환
        return jsonify({
            "status": "success",
            "message": f"Container '{container_name}' has been deleted successfully."
        }), 200  # HTTP 상태 코드 200
    except Exception as e:
        # 오류 처리
        return jsonify({
            "status": "error",
            "message": f"Failed to delete container '{container_name}': {str(e)}"
        }), 500  # HTTP 상태 코드 500


    
    
    