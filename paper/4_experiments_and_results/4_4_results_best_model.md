제 4 절 결과 분석 및 최적 모델 선정
시계열 예측에는 통계적 모형부터 최신 기계학습 기반 모형까지 다양한 접근법이 활용된다
본 연구에서 수행한 일련의 실험과 분석을 종합하여 PM2.5 농도 예측을 위한 최적 모델을 선정하고, 그 타당성을 제시한다.
(1) 최적 모델 선정
앞서 진행한 기본 모델 비교와 LLM 기반 하이퍼파라미터 튜닝 결과를 종합적으로 고려할 때, LLM 튜닝을 거친 LSTM 모델을 최적 모델로 선정한다. 이 모델은 RMSE 2.77, MAE 2.22, R² 0.94, MAPE 12.31%의 성능 지표를 달성하였으며, 이는 다른 모든 모델 및 변형보다 우수한 결과이다. 특히 기본 LSTM 모델(RMSE 4.57) 대비 약 39.49%의 예측 오차 감소, 그리고 튜닝 전 가장 우수했던 Transformer 모델(RMSE 3.66) 대비 약 24.32%의 성능 향상을 보였다.
(2) 선정 근거
LLM 튜닝 LSTM 모델을 최적 모델로 선정한 주요 근거는 다음과 같다:
우수한 예측 정확도: 모든 평가 지표에서 최고 성능을 달성하였다. 특히 MAPE 12.31%는 실제값의 약 12% 내외 오차로 예측함을 의미하며, 이는 실용적 관점에서 상당히 신뢰할 만한 수준이다.
높은 설명력: R² 0.94는 모델이 PM2.5 농도 변동의 94%를 설명할 수 있음을 의미한다. 이는 매우 높은 수준으로, 시계열 데이터의 복잡한 패턴과 변동성을 효과적으로 포착할 수 있음을 보여준다.
데이터 특성과의 적합성: 제1절에서 분석한 PM2.5 데이터의 특성(강한 일중 주기성, 다수의 구조적 변화점, 비선형 패턴)을 고려할 때, LSTM의 구조적 특성이 이러한 데이터 특성을 효과적으로 모델링할 수 있다. 특히 LLM 튜닝에서 제안된 48시간의 입력 시퀀스는 24시간 주기성과 함께 좀 더 장기적인 패턴을 포착할 수 있는 적절한 설계이다.
계산 효율성과 복잡도 균형: 튜닝된 LSTM 모델은 두 층 구조([64, 32] 유닛)로 Transformer보다 계산 효율성이 좋으면서도, 충분한 표현력을 갖추고 있다. 이는 실시간 예측 시스템 구축 시 계산 자원 효율성 측면에서 이점이 있다.
(3) 최적 모델 구조 및 구성
LLM 튜닝을 통해 최종 선정된 LSTM 모델의 구조 및 하이퍼파라미터는 표 5와 같다.
<표 5> 최적 모델(LLM 튜닝 LSTM)의 구조 및 하이퍼파라미터
하이퍼파라미터	값	설명
lstm_units	[64, 32]	두 개의 LSTM 층 구성(64개, 32개 유닛)
n_steps	48	과거 48시간 데이터 기반 예측
dropout	0.2	과적합 방지를 위한 드롭아웃 비율
batch_size	32	배치 크기
learning_rate	0.001	학습률
epochs	100	최대 학습 반복 횟수(조기 종료 적용)
이러한 구성은 PM2.5 데이터의 일중 주기성을 2일(48시간) 단위로 고려하여 보다 장기적인 패턴을 포착할 수 있게 하며, 두 층 구조와 적절한 드롭아웃 비율을 통해 과적합을 방지하면서도 복잡한 비선형 관계를 학습할 수 있다.
(4) 모델 선정의 실용적 의의
최적 모델로 선정된 LLM 튜닝 LSTM은 다음과 같은 실용적 의의를 가진다:
실시간 대기질 예측 가능성: MAPE 12.31%의 예측 정확도는 실시간 대기질 모니터링 및 예측 시스템에 충분히 활용 가능한 수준이다. 이는 환경 정책 결정이나 시민 대상 대기질 경보 시스템에 유용하게 적용될 수 있다.
범용성과 확장성: 본 연구에서 개발한 LLM 기반 튜닝 LSTM 모델은 다른 유사한 시계열 예측 문제(예: 다른 대기 오염물질, 에너지 수요 예측 등)에도 적용 가능한 범용적 접근법이다.
해석 가능성 확보: 기존 딥러닝 모델의 한계로 지적되는 해석 가능성 문제를 LLM이 생성한 모델 분석 보고서를 통해 일부 보완할 수 있다. 이는 전문가가 아닌 이해관계자들도 모델 결과를 이해하고 활용하는 데 도움이 된다.
(5) 다른 모델과의 차별점
최적 모델로 선정된 LLM 튜닝 LSTM은 다른 후보 모델들과 비교하여 다음과 같은 차별점을 갖는다:
통계 기반 모델(지수평활법, ARIMA, Prophet)은 LLM 튜닝 후에도 R² 및 MAPE 지표가 실용적 활용에 부적합한 수준이었다. 비록 LLM 튜닝이 이들 모델의 성능을 크게 향상시켰지만, PM2.5 시계열의 복잡한 비선형 패턴을 완전히 포착하지는 못했다.
Transformer 모델은 기본 구성에서 우수한 성능을 보였으나, LLM이 제안한 복잡한 구조로 변경 후 오히려 성능이 저하되었다. 이는 데이터 양 대비 모델 복잡도 증가가 과적합을 초래했을 가능성을 시사하며, 현재 데이터셋 규모에서는 LSTM이 더 적합한 균형점을 제공함을 보여준다.
결론적으로, LLM 튜닝 LSTM 모델은 예측 정확도, 계산 효율성, 데이터 특성과의 적합성, 그리고 실용적 활용 가능성 등 여러 측면에서 균형 잡힌 최적의 선택이라 할 수 있다. 이 모델은 PM2.5 농도의 일중 변동, 단기 추세, 급격한 변화 등을 효과적으로 포착하면서도, 실시간 예측 시스템 구현에 적합한 효율성을 갖추고 있다.
