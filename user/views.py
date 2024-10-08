from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from .forms import SignUpForm, ProfileFormPage1, ProfileFormPage2, ProfileFormPage3, ProfileFormPage4
from .models import Profile, WeeklyPlan, MealRecord
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import openai
from dotenv import load_dotenv
from datetime import datetime, timedelta
import os
import json
import re

load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('home') 
    else:
        form = SignUpForm() 
    return render(request, 'user/signup.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def profile_create_step1(request):
    try:
        # 프로필이 이미 있는지 확인
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        # 프로필이 없으면 새로 생성할 준비
        profile = None

    if request.method == 'POST':
        form = ProfileFormPage1(request.POST, instance=profile)  # 기존 프로필을 업데이트하도록 함
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect('user:profile_create_step2')
    else:
        form = ProfileFormPage1(instance=profile)  # 기존 프로필이 있으면 해당 내용을 폼에 넣어줌
    return render(request, 'user/profile_step1.html', {'form': form})

@login_required
def profile_create_step2(request):
    try:
        # 프로필이 이미 있는지 확인
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        # 프로필이 없으면 새로 생성할 준비
        profile = None

    if request.method == 'POST':
        form = ProfileFormPage2(request.POST)
        if form.is_valid():
            profile = Profile.objects.get(user=request.user)
            profile.height = form.cleaned_data['height']
            profile.weight = form.cleaned_data['weight']
            profile.medical_history = form.cleaned_data['medical_history']
            profile.save()
            return redirect('user:profile_create_step3')
    else:
        form = ProfileFormPage2()
    return render(request, 'user/profile_step2.html', {'form': form})

@login_required
def profile_create_step3(request):
    try:
        # 프로필이 이미 있는지 확인
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        # 프로필이 없으면 새로 생성할 준비
        profile = None

    if request.method == 'POST':
        form = ProfileFormPage3(request.POST)
        if form.is_valid():
            profile = Profile.objects.get(user=request.user)
            profile.dietary_habits = form.cleaned_data['dietary_habits']
            profile.activity_level = form.cleaned_data['activity_level']
            profile.sleep_hours = form.cleaned_data['sleep_hours']
            profile.save()
            return redirect('user:profile_create_step4')
    else:
        form = ProfileFormPage3()
    return render(request, 'user/profile_step3.html', {'form': form})

@login_required
def profile_create_step4(request):
    try:
        # 프로필이 이미 있는지 확인
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        # 프로필이 없으면 새로 생성할 준비
        profile = None
        
    if request.method == 'POST':
        form = ProfileFormPage4(request.POST)
        if form.is_valid():
            profile = Profile.objects.get(user=request.user)
            profile.goal_weight = form.cleaned_data['goal_weight']
            profile.goal_strength = form.cleaned_data['goal_strength']
            profile.goal_deadline = form.cleaned_data['goal_deadline']
            profile.save()
            return redirect('user:profile_complete')
    else:
        form = ProfileFormPage4()
    return render(request, 'user/profile_step4.html', {'form': form})

@login_required
def profile_complete(request):
    return render(request, 'user/profile_complete.html')

def extract_meal_info(gpt_response):
    """
    GPT 응답에서 요일별 식사 정보를 JSON 형식으로 추출.
    """
    weekly_plan = {}

    # 요일 리스트
    days_of_week = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']

    # 정규식 패턴: "요일 아침/점심/저녁 식사:" 부분을 제거하고 실제 식사 정보만 추출
    pattern = re.compile(r"([가-힣]+) (아침 식사|점심 식사|저녁 식사|운동 계획):\s*(.*)")

    # 정규식으로 매칭된 결과에서 정보를 추출하여 JSON 형식으로 변환
    matches = pattern.findall(gpt_response)
    for match in matches:
        day, plan_type, plan_info = match
        if day not in weekly_plan:
            weekly_plan[day] = {}
        # 각 계획을 해당 요일에 맞게 저장
        if plan_type == '아침 식사':
            weekly_plan[day]['아침'] = plan_info.strip()
        elif plan_type == '점심 식사':
            weekly_plan[day]['점심'] = plan_info.strip()
        elif plan_type == '저녁 식사':
            weekly_plan[day]['저녁'] = plan_info.strip()
        elif plan_type == '운동 계획':
            weekly_plan[day]['운동 계획'] = plan_info.strip()

    return weekly_plan

# 처음 식단, 운동 계획표 작성
def generate_weekly_plan(profile):
    messages = [
        {
            "role": "system",
            "content": "당신은 맞춤형 주간 식단 계획을 생성하는 어시스턴트입니다. 각 식사에 대해 정확한 g 단위의 양을 포함하여 주어진 형식에 맞춰서 반환하세요. 형식에 맞춰서만 응답하세요."
        },
        {
            "role": "user",
            "content": f"""
            다음 사용자를 위한 주간 식단 계획을 생성하세요:
            - 이름: {profile.name}
            - 나이: {profile.age}
            - 키: {profile.height} cm
            - 몸무게: {profile.weight} kg
            - 식습관: {profile.dietary_habits}
            - 운동 습관: {profile.activity_level}
            - 선호 운동: {profile.prefer_activity}
            - 목표: {profile.goal_strength}, 기한: {profile.goal_deadline}

            주간 계획은 요일별로 작성되어야 하며, 각 요일에 대해 아침, 점심, 저녁 식사의 정확한 g 단위의 양을 포함하세요. 운동 계획은 선호 운동 위주로 가능하면 자세하게 작성해주세요. 다른 텍스트 없이 형식에 맞춰서 생성해주세요. 각 형식에는 다음을 포함해야 합니다:
            - 요일(월요일부터 일요일까지)
            - 아침 식사 메뉴(g 단위의 정확한 양 포함)
            - 점심 식사 메뉴(g 단위의 정확한 양 포함)
            - 저녁 식사 메뉴(g 단위의 정확한 양 포함)
            - 운동 계획

            - 형식 -

            월요일 아침 식사:
            월요일 점심 식사:
            월요일 저녁 식사:
            월요일 운동 계획:

            화요일 아침 식사:
            화요일 점심 식사:
            화요일 저녁 식사:
            화요일 운동 계획:
            """
        }
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=1500
    )

    gpt_response = response.choices[0].message['content']

    # gpt_response에서 각 요일별로 데이터를 추출하여 JSON 형식으로 변환
    weekly_plan_json = extract_meal_info(gpt_response)

    # 식사별 영양소 정보 추출
    

    # 주간 계획을 JSON 형식으로 반환
    return weekly_plan_json

# 지난 주 식단 운동 기록 반영 작성
def adjust_weekly_plan(profile, last_week_records):
    # 지난 주 식단 기록에서 각 영양소의 차이를 계산
    total_calorie_diff = sum(record.calorie_difference for record in last_week_records)
    total_protein_diff = sum(record.protein_difference for record in last_week_records)
    total_carb_diff = sum(record.carb_difference for record in last_week_records)
    total_fat_diff = sum(record.fat_difference for record in last_week_records)

    # GPT-4o에 전달할 메시지 구성
    messages = [
        {
            "role": "system",
            "content": "당신은 사용자의 실제 식단 기록을 바탕으로 맞춤형 주간 식단을 조정하는 어시스턴트입니다. 주어진 정보를 바탕으로 다음 주 식단 계획을 조정하세요."
        },
        {
            "role": "user",
            "content": f"""
            다음 사용자를 위한 주간 식단 계획을 조정하세요:
            - 이름: {profile.name}
            - 나이: {profile.age}
            - 키: {profile.height} cm
            - 몸무게: {profile.weight} kg
            - 식습관: {profile.dietary_habits}
            - 운동 습관: {profile.activity_level}
            - 선호 운동: {profile.prefer_activity}
            - 목표: {profile.goal_strength}, 기한: {profile.goal_deadline}

            사용자 {profile.name}는 지난 주에 계획보다 {total_calorie_diff} 칼로리, {total_protein_diff}g 단백질, {total_carb_diff}g 탄수화물, {total_fat_diff}g 지방을 더/덜 섭취했습니다.
            이번 주의 식단은 목표 기한 내에 {profile.goal_strength}을 달성하기 위해 조정되어야 하며, 특히 지난 주의 영양소 차이를 보완해야 합니다.

            주간 계획은 요일별로 작성되어야 하며, 각 요일에 대해 아침, 점심, 저녁 식사의 정확한 g 단위의 양을 포함하세요. 운동 계획은 선호 운동 위주로 가능하면 자세하게 작성해주세요. 다른 텍스트 없이 형식에 맞춰서 생성해주세요. 각 형식에는 다음을 포함해야 합니다:
            - 요일(월요일부터 일요일까지)
            - 아침 식사 메뉴(g 단위의 정확한 양 포함)
            - 점심 식사 메뉴(g 단위의 정확한 양 포함)
            - 저녁 식사 메뉴(g 단위의 정확한 양 포함)
            - 운동 계획

            - 형식 -

            월요일 아침 식사:
            월요일 점심 식사:
            월요일 저녁 식사:
            월요일 운동 계획:

            화요일 아침 식사:
            화요일 점심 식사:
            화요일 저녁 식사:
            화요일 운동 계획:
            """
        }
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4o",  # GPT-4o 모델 지정
        messages=messages,  # 메시지 리스트 전달
        max_tokens=1500  # 충분한 텍스트를 받을 수 있도록 설정
    )

    gpt_response = response.choices[0].message['content']

    # gpt_response에서 각 요일별로 데이터를 추출하여 배열로 저장
    weekly_plan_array = extract_meal_info(gpt_response)

    # 주간 계획 배열을 바로 반환 (JSON 형태로 저장되도록 처리)
    return weekly_plan_array

# 로그인 할 시 프로필 존재 여부 판단
@login_required
def check_profile(request):
    try:
        profile = Profile.objects.get(user=request.user)
        # 프로필이 존재하는 경우, 원하는 페이지로 이동
        return redirect('home')  # 홈 페이지로 이동 또는 다른 페이지로 변경
    except Profile.DoesNotExist:
        # 프로필이 없는 경우, 프로필 입력 첫 페이지로 이동
        return redirect('user:profile_create_step1')
    
# 일주일 날짜 판단
def get_week_range():
    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday())  # 이번 주 월요일
    end_of_week = start_of_week + timedelta(days=6)  # 이번 주 일요일
    return start_of_week.date(), end_of_week.date()

# 시간표 뷰
@login_required
def weekly_plan(request):
    # 이번 주의 월요일과 일요일 날짜를 가져옴
    start_of_week, end_of_week = get_week_range()

    # 사용자의 이번 주 주간 계획표가 있는지 확인
    weekly_plan = WeeklyPlan.objects.filter(user=request.user, start_date=start_of_week, end_date=end_of_week).first()

    if not weekly_plan:
        # 주간 계획표가 없으면 새로운 주간 계획표를 생성해야 함
        last_week_start, last_week_end = start_of_week - timedelta(weeks=1), end_of_week - timedelta(weeks=1)

        # 지난 주 식단 기록을 가져옴
        last_week_records = MealRecord.objects.filter(user=request.user, date__range=[last_week_start, last_week_end])

        if last_week_records.exists():
            # 지난 주 식단 기록이 있으면 이를 바탕으로 주간 계획을 조정
            plan_content = adjust_weekly_plan(request.user.profile, last_week_records)
        else:
            # 지난 주 기록이 없으면 새로운 주간 계획 생성
            plan_content = generate_weekly_plan(request.user.profile)

        # 식사별 영양소 정보 추출
        nutrition_info_json = extract_nutrition_info_for_meals(plan_content)

        # 생성된 계획을 JSON 형식으로 저장
        weekly_plan = WeeklyPlan.objects.create(
            user=request.user,
            start_date=start_of_week,
            end_date=end_of_week,
            plan_content=plan_content,  # 식단 계획 JSON 저장
            nutrition_info=nutrition_info_json  # 영양 정보 JSON 저장
        )

    else:
        # 이미 있는 주간 계획을 JSON 형식으로 가져옴
        plan_content = weekly_plan.plan_content
        nutrition_info_json = weekly_plan.nutrition_info

    # 주간 계획을 화면에 출력
    return render(request, 'user/weekly_plan.html', {'plan': plan_content, 'nutrition': nutrition_info_json})


def extract_nutrition_info_for_meals(weekly_plan_json):
    """
    각 식사별로 GPT API를 사용하여 탄수화물, 단백질, 지방 정보를 추출한 후 반환하는 함수.
    """
    nutrition_info = {}

    for day, meals in weekly_plan_json.items():
        nutrition_info[day] = {}
        
        for meal_time, meal_menu in meals.items():
            if meal_time in ['아침', '점심', '저녁']:  # 운동 계획은 제외
                # GPT API로 식사 메뉴에 대한 영양소 정보 추출
                nutrition_data = fetch_nutrition_info_from_gpt(meal_menu)
                # 영양소 정보를 해당 요일과 식사 시간에 맞게 저장
                nutrition_info[day][meal_time] = nutrition_data

    return nutrition_info


def fetch_nutrition_info_from_gpt(meal_menu):
    """
    GPT API를 호출하여 주어진 식사 메뉴에 대한 영양소 정보를 추출하는 함수.
    반환 값은 탄수화물, 단백질, 지방을 포함한 딕셔너리.
    """
    try:
        # GPT에게 식사 메뉴에 대해 탄수화물, 단백질, 지방 정보를 요청하는 메시지 구성
        messages = [
            {
                "role": "system",
                "content": "당신은 식사의 영양 정보를 제공하는 전문가입니다. 각 식사 메뉴에 대해 탄수화물, 단백질, 지방의 양을 정확하게 계산해 주세요. 모든 식사 메뉴에는 탄수화물, 단백질, 지방이 0g인 경우가 없도록 계산해야 하며, 올바른 영양 정보에 따라 반환해야 합니다."
            },
            {
                "role": "user",
                "content": f"""
                다음 식사의 탄수화물, 단백질, 지방을 각각 g 단위로 계산해 주세요. 반드시 식사 전체에 대한 영양 정보를 합산하여 출력하고, 다른 추가적인 설명은 포함하지 마세요. 결과는 반드시 아래 형식만 사용하세요:

                - 탄수화물: [숫자]g
                - 단백질: [숫자]g
                - 지방: [숫자]g

                모든 식사는 0g인 경우가 없어야 하며, 음식의 특성을 고려해 정확하게 계산해 주세요.

                식사: {meal_menu}
                """
            }
        ]

        # GPT API 호출
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=150
        )

        # GPT의 응답을 JSON으로 파싱
        gpt_response = response.choices[0].message['content']
        nutrition_info = parse_nutrition_info(gpt_response)
        
        return nutrition_info
    except Exception as e:
        print(f"Error fetching nutrition info from GPT: {e}")
        return {"carbs": 0, "protein": 0, "fat": 0}


# DB에 날짜 저장을 위한 필드
@csrf_exempt
def get_nutrition(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        day = body.get('day', '')
        breakfast = body.get('breakfast', '')
        lunch = body.get('lunch', '')
        dinner = body.get('dinner', '')

        meal_date = convert_day_to_date(day)

        # 주간 계획표 가져오기 (이때 주간 계획표에는 이미 저장된 영양 정보가 있어야 함)
        weekly_plan = WeeklyPlan.objects.filter(user=request.user, start_date__lte=meal_date, end_date__gte=meal_date).first()

        # 해당 날짜에 대한 영양 정보가 저장된 weekly_plan이 있는지 확인
        if not weekly_plan or not weekly_plan.nutrition_info:
            return JsonResponse({'error': '주간 식단 정보가 없습니다.'}, status=400)

        nutrition_info_json = weekly_plan.nutrition_info

        # 각 식사에 대해 GPT를 사용해 영양 정보 추출 후 DB에 저장
        if breakfast:
            nutrition_info = fetch_nutrition_info_from_gpt(breakfast)
            plan_nutrition = nutrition_info_json.get(day, {}).get('아침', {})  # 주간 계획의 아침 영양 정보
            save_meal_record_with_difference(request.user, meal_date, 'breakfast', breakfast, nutrition_info, plan_nutrition)

        if lunch:
            nutrition_info = fetch_nutrition_info_from_gpt(lunch)
            plan_nutrition = nutrition_info_json.get(day, {}).get('점심', {})  # 주간 계획의 점심 영양 정보
            save_meal_record_with_difference(request.user, meal_date, 'lunch', lunch, nutrition_info, plan_nutrition)

        if dinner:
            nutrition_info = fetch_nutrition_info_from_gpt(dinner)
            plan_nutrition = nutrition_info_json.get(day, {}).get('저녁', {})  # 주간 계획의 저녁 영양 정보
            save_meal_record_with_difference(request.user, meal_date, 'dinner', dinner, nutrition_info, plan_nutrition)

        return JsonResponse({'message': '식사 정보가 저장되었습니다.'})

    elif request.method == 'GET':
        # 저장된 식사 정보를 요청할 경우
        day = request.GET.get('day', '')

        meal_date = convert_day_to_date(day)

        # 기존에 입력된 데이터를 DB에서 불러옴
        breakfast_record = MealRecord.objects.filter(user=request.user, date=meal_date, meal_type='breakfast').first()
        lunch_record = MealRecord.objects.filter(user=request.user, date=meal_date, meal_type='lunch').first()
        dinner_record = MealRecord.objects.filter(user=request.user, date=meal_date, meal_type='dinner').first()

        response_data = {}

        # 각각 아침, 점심, 저녁 데이터를 추가로 불러오기
        if breakfast_record:
            response_data['breakfast'] = {
                'actual_food': breakfast_record.actual_food,
                'carbs': breakfast_record.carb_difference or 0,
                'protein': breakfast_record.protein_difference or 0,
                'fat': breakfast_record.fat_difference or 0
            }

        if lunch_record:
            response_data['lunch'] = {
                'actual_food': lunch_record.actual_food,
                'carbs': lunch_record.carb_difference or 0,
                'protein': lunch_record.protein_difference or 0,
                'fat': lunch_record.fat_difference or 0
            }

        if dinner_record:
            response_data['dinner'] = {
                'actual_food': dinner_record.actual_food,
                'carbs': dinner_record.carb_difference or 0,
                'protein': dinner_record.protein_difference or 0,
                'fat': dinner_record.fat_difference or 0
            }

        # 응답 데이터가 비어있으면 메시지를 반환
        if not response_data:
            return JsonResponse({'message': '저장된 정보가 없습니다.'})

        return JsonResponse(response_data)

    return JsonResponse({'error': 'Invalid request'}, status=400)

# 실제 식사에 대한 영양소 정보 차이를 저장하는 함수
def save_meal_record_with_difference(user, date, meal_type, actual_food, nutrition_info, plan_nutrition):
    try:
        # 주간 식단과 비교하여 차이를 계산 (계획된 값이 없는 경우 기본값 0)
        carb_diff = nutrition_info.get('carbs', 0) - plan_nutrition.get('carbs', 0)
        protein_diff = nutrition_info.get('protein', 0) - plan_nutrition.get('protein', 0)
        fat_diff = nutrition_info.get('fat', 0) - plan_nutrition.get('fat', 0)

        # DB에 MealRecord 저장 또는 업데이트
        meal_record, created = MealRecord.objects.update_or_create(
            user=user,
            date=date,
            meal_type=meal_type,
            defaults={
                'actual_food': actual_food,
                'carb_difference': carb_diff,
                'protein_difference': protein_diff,
                'fat_difference': fat_diff
            }
        )
    except Exception as e:
        print(f"Error saving meal record: {e}")

# 날짜 변환 함수
def convert_day_to_date(day):
    """
    사용자가 입력한 요일을 실제 날짜로 변환
    """
    import datetime
    today = datetime.date.today()
    days = {'월요일': 0, '화요일': 1, '수요일': 2, '목요일': 3, '금요일': 4, '토요일': 5, '일요일': 6}
    delta = days[day] - today.weekday()
    return today + datetime.timedelta(days=delta)


# GPT로부터 받은 응답을 파싱하여 탄수화물, 단백질, 지방 정보를 반환하는 함수
def parse_nutrition_info(gpt_response):
    try:
        # 정규식을 사용하여 탄수화물, 단백질, 지방 값을 추출
        carb_match = re.search(r'탄수화물:\s*(\d+)g', gpt_response)
        protein_match = re.search(r'단백질:\s*(\d+)g', gpt_response)
        fat_match = re.search(r'지방:\s*(\d+)g', gpt_response)
        
        # 추출된 값을 정수로 변환하여 반환
        return {
            'carbs': int(carb_match.group(1)) if carb_match else 0,
            'protein': int(protein_match.group(1)) if protein_match else 0,
            'fat': int(fat_match.group(1)) if fat_match else 0
        }
    except Exception as e:
        print(f"Error parsing nutrition info: {e}")
        return {'carbs': 0, 'protein': 0, 'fat': 0}
