목    차
제 Ⅰ 장 서 론 	1
제 1절 연구의 배경 및 목적	1
제 2절 연구 범위 및 방법	2
제 3절 논문의 구성	3
제 Ⅱ 장 이론적 배경 	4
제 1절 시계열 예측 모델 개요	4
제 2절 하이퍼파라미터 튜닝과 AutoML	8
제 3절 생성형 AI와 시계열 분석	10
제 Ⅲ 장 연구 방법 	13
제 1절 연구 설계 및 절차	13
(1) 연구 개요	13
(2) 시스템 구성	15
1) 데이터 준비 모듈	15
2) 예측 모델 학습 모듈	15
3) LLM 프롬프트 모듈	15
4) 평가/피드백 모듈	15
제 2절 데이터 수집 및 실험 설계	16
(1) 데이터 수집	16
(2) 실험 설계	17
제 3절 시계열 예측 모델 구성 및 학습	19
(1) 모델 구성 요소	19
(2) 학습 하이퍼파라미터 설정	21
제 4절 LLM 기반 모델링 자동화 및 프롬프트 설계	23
(1) LLM 선택 및 실행 방식	23
(2) 프롬프트 설계 및 예시	24
1) 프롬프트 예시 (LSTM 모델)	25
2) LLM 응답 예시	26
(3) LLM 기반 하이퍼파라미터 튜닝 피드백 루프	27
(4) 재현성과 신뢰성 확보 방안	29
(5) 자동 분석 보고서 생성	31
제 5절 실험 환경 및 구현 세부 사항	33
(1) 하드웨어 및 소프트웨어 환경	33
1) 하드웨어 구성	33
2) 소프트웨어 환경	33
(2) 시스템 아키텍처 설계	34
1) 모델 추상화 설계	34
2) LLM 연동 아키텍처	35
(3) 모델 구현 세부사항	35
1) ARIMA/SARIMA 모델	35
2) 지수형활법 모델	36
3) Prophet 모델	37
4) LSTM 모델	37
5) Transformer 모델	37
(4) 데이터 처리 파이프라인	38
1) 데이터 수집	38
2) 데이터 전처리	38
3) 시계열 변환 및 분석	39
(5) LLM 활용 자동화 구현	39
1) 하이퍼파라미터 최적화 프로세스	39
2) 분석 보고서 자동 생성	40
(6) 사용자 인터페이스 구현	40
(7) 재현성 및 신뢰성 확보 방안	41
제 Ⅳ 장 실험 및 결과 	42
제 1절 실험 설정	42
(1) 데이터 수집 및 특성	42
(2) 데이터 기초 통계 분석	43
1) 기술 통계량	43
(3) 시계열 특성 분석	44
1) 시계열 분해 분석	44
2) 정상성 검정	45
3) 자기상관 분석	45
(4) 구조적 변화점 분석	46
(5) 변수 간 상관관계 및 인과성 분석	47
(6) 평가 지표 선정	48
제 2절 모델별 성능 비교 	49
(1) 성능 평가 지표 분석	49
1) RMSE(Root Mean Squared Error)	50
2) MAE(Mean Absolute Error)	50
3) R2(결정계수)	51
4) MAPE(Mean Absolute Percentage Error)	51
(2) 모델별 예측 성능 분석	51
1) 지수평활법	52
2) ARIMA/SARIMA 모델	52
3) Prophet 모델	52
4) LSTM 모델	53
5) Transformer 모델	53
(3) 모델 간 성능 비교 분석	54
1) 딥러닝 모델과 통계 모델 간 성능 격차	54
2) Transformer와 LSTM의 우수성	55
3) 통계 모델의 한계점	55
4) 모델 복잡도와 성능의 관계	55
(4) 데이터 특성과 모델 정합성	56
1) 구조적 변화 대응 능력	57
2) 비선형 패턴 학습 능력	57
3) 장기 의존성 포착 능력	58
4) 계산 효율성과 실용성	58
제 3절 LLM 기반 하이퍼파라미터 튜닝 결과	59
(1) 모델별 LLM 하이퍼파라미터 튜닝 제안	59
(2) 튜닝 결과 및 성능 향상 분석	59
(3) LLM 튜닝의 유효성 및 시사점	64
제 4절 결과 분석 및 최적 모델 선정 	65
(1) 최적 모델 선정	66
(2) 선정 근거	66
(3) 최적 모델 구조 및 구성	67
(4) 모델 선정의 실용적 의의	68
(5) 다른 모델과의 차별점	68
제 Ⅴ 장 결론 및 향후 연구 	70
제 1절 연구 결과 요약	70
제 2절 연구의 시사점	71
제 3절 연구의 한계 및 향후 연구 방향	73

참고문헌 	75
