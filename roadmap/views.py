import os
import requests
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import Bookmark
from dotenv import load_dotenv
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from django.core.paginator import Paginator

# .env 파일 로드
load_dotenv()

@csrf_exempt
def map(request):
    # GET 요청을 받을 때 페이지네이션 처리
    if request.method == "GET":
        try:
            user_lat = request.GET.get('lat', 37.551626)  # 기본 위치 값 설정
            user_lng = request.GET.get('lng', 126.928127)
            page_number = request.GET.get('page', 1)  # 현재 페이지 번호를 가져옴 (기본값 1)
            print("사용자 위치:", user_lat, user_lng)

            # 카카오 지도 API를 사용해 운동 시설 검색
            headers = {
                "Authorization": f"KakaoAK {os.getenv('KAKAO_REST_API_KEY')}"
            }
            params = {
                "query": "헬스장",  # 검색 키워드를 적절히 설정하세요 (한글로 입력 가능)
                "x": user_lng,
                "y": user_lat,
                "radius": 20000,  # 반경 20km 내 검색
                "page": page_number,
                "size": 15  # 한 페이지당 5개의 결과 표시
            }
            response = requests.get("https://dapi.kakao.com/v2/local/search/keyword.json", headers=headers, params=params)
            print("응답 상태 코드:", response.status_code)
            print("응답 데이터:", response.text)

            if response.status_code != 200:
                return JsonResponse({'error': 'Failed to get data from Kakao API'}, status=500)

            data = response.json()

            # 운동 시설 목록 파싱
            facilities = []
            if "documents" in data:
                for document in data["documents"]:
                    facilities.append({
                        "id": document.get("id"),
                        "name": document.get("place_name"),
                        "address": document.get("road_address_name"),
                        "lat": document.get("y"),
                        "lng": document.get("x"),
                        "detail_url": document.get("place_url")
                    })

            # 페이지네이션 적용
            paginator = Paginator(facilities, 15)  # 한 페이지당 5개의 시설 표시
            page_number = request.GET.get('page', 1)
            page_obj = paginator.get_page(page_number)

            context = {
                'facilities': page_obj.object_list,  # 현재 페이지의 시설 리스트
                'pagination': page_obj,  # 페이지네이션 객체
                'kakao_map_client_key': os.getenv("KAKAO_JS_API_KEY"),
            }

            return render(request, 'roadmap/map.html', context)

        except Exception as e:
            print(f'Error: {str(e)}')
            return JsonResponse({'error': str(e)}, status=500)

    # 기본 GET 요청 처리 (처음 페이지 렌더링 시)
    else:
        context = {
            'kakao_map_client_key': os.getenv("KAKAO_JS_API_KEY"),
        }
        return render(request, 'roadmap/map.html', context)