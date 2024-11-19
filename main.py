import streamlit as st
import openai
import json
import os
import random
from dotenv import load_dotenv


# Set the OpenAI API key
openai.api_key = api_key

if not api_key:
    raise ValueError("API 키가 설정되지 않았습니다. .env 파일을 확인하세요.")

openai.api_key = api_key

# JSON 데이터 로드 함수
@st.cache_data
def load_json_data(file_name):
    """JSON 파일을 로드하는 함수."""
    with open(file_name, 'r', encoding='utf-8') as file:
        return json.load(file)

# JSON 데이터 샘플링 함수
def sample_json_data(data, sample_size=5):
    """샘플 데이터 추출 함수."""
    return data[:sample_size] if len(data) > sample_size else data

import random

# 이벤트 생성 함수
def generate_event(goal, strategy, audience, budget, data, temperature=0.7, max_tokens=300):
    """OpenAI를 사용하여 이벤트 기획안을 생성하는 함수."""
    # 사용자가 선택한 max_tokens 값에 ±30 범위로 랜덤 설정
    adjusted_max_tokens = random.randint(max(100, max_tokens - 30), min(800, max_tokens + 30))

    messages = [
        {"role": "system", "content": "You are an expert event planner specializing in cosmetics."},
        {"role": "user", "content": f"""
        I need a cosmetics-related event plan that achieves the following:

        - **Goal**: {goal}
        - **Strategy**: {strategy}
        - **Target Audience**: {audience}
        - **Budget**: {budget}

        Use the provided product data as a reference:
        {data}

        Please ensure the event plan aligns with the budget and appeals to the specified audience. Include specific product recommendations, promotional strategies, and detailed implementation steps. If the budget is too complex or unclear, make reasonable assumptions and explain them.
        """}
    ]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=adjusted_max_tokens,  # 랜덤으로 설정된 토큰 값 사용
        temperature=temperature
    )
    return response['choices'][0]['message']['content'].strip(), adjusted_max_tokens

# Streamlit 앱 구성
def main():
    st.title("Cosmetics Event Planner")
    st.write("Enter the details below to generate a customized event plan:")

    # 입력 필드를 폼으로 구성
    with st.form("event_form"):
        goal = st.text_input("Goal (목표)", "")
        strategy = st.text_input("Strategy (전략)", "")
        audience = st.text_input("Target Audience (타겟층)", "")
        budget = st.text_input("Budget (예산)", "")
        temperature = st.slider("Creativity Level (Temperature)", 0.0, 1.0, 0.7)
        max_tokens = st.slider("Set Max Tokens", 100, 800, 300)  # 기본값 300
        submit = st.form_submit_button("Generate Event Plan")

    # JSON 파일 로드 및 샘플링
    json_file_name = "cosmetics_data.json"
    try:
        cosmetics_data = load_json_data(json_file_name)
        cosmetics_data = sample_json_data(cosmetics_data, sample_size=10)  # 샘플 크기를 조정하세요.
    except FileNotFoundError:
        st.error(f"JSON 파일 '{json_file_name}'을(를) 찾을 수 없습니다.")
        return
    except json.JSONDecodeError:
        st.error(f"JSON 파일이 잘못된 형식입니다. 파일 내용을 확인해주세요.")
        return

    # 입력 필드가 채워졌는지 확인
    if submit:
        if not all([goal, strategy, audience, budget]):
            st.warning("모든 필드를 입력해주세요.")
            return

        # 데이터 문자열로 변환
        data_str = "\n".join([f"{item['브랜드명']} - {item['제품명']} ({item['모든성분']})" for item in cosmetics_data])

        # 이벤트 플랜 생성
        event_plan, used_max_tokens = generate_event(goal, strategy, audience, budget, data_str, temperature, max_tokens)

        # 결과 출력
        st.markdown("### Generated Event Plan")
        st.markdown(f"**1. 목표**\n{goal}")
        st.markdown(f"**2. 타겟층**\n{audience}")
        st.markdown(f"**3. 전략**\n{strategy}")
        st.markdown(f"**4. 이벤트 기획안**\n{event_plan.replace('\n', '\n\n')}")
        st.markdown(f"**5. 예산**\n{budget}")
        st.markdown(f"**6. 실행 가이드**\n행사 진행 시 소비자들이 제품을 직접 경험할 수 있도록 설계하세요. 적절한 장비와 인력을 활용해 성공적인 이벤트를 만드세요.")
        st.markdown(f"**7. 사용된 토큰 제한**: {used_max_tokens} tokens")

if __name__ == "__main__":
    main()
    
