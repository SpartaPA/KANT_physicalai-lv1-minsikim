# 모듈 ④ 발표 자료 — 픽앤플레이스 자세 추정과 궤적 생성

> 이름: 김민식 / 제출일: 2026-09-11

---

## 1. 파이프라인 전체 구조

- 좌표계 체인 (base -> link -> camera -> object) 그림 또는 다이어그램:
  `[base] --(T_base_link)--> [link] --(T_link_cam)--> [camera] --(T_cam_obj)--> [object]`
- 각 노트북·모듈이 맡는 역할 (01 파이프라인 / 02 보간 / 03 자세 추정·시연):
  - **01 파이프라인:** Forward Kinematics 및 순차 동차변환(T) 행렬을 이용한 좌표계 체인(FK Chain) 구축 및 좌표 변환
  - **02 보간:** 쿼터니언 SLERP 기반의 회전 보간 및 Cubic Spline / Linear 보간 기반의 다중 경유점(Waypoint) 위치 궤적 생성
  - **03 자세 추정·시연:** PCA를 이용한 주축 추출, Kabsch 알고리즘 및 최소제곱(Lstsq) 평면 피팅 기반 자세 추정/이상치 제거, 픽앤플레이스 궤적 애니메이션 생성 및 `demo.gif` 저장
- 데이터 흐름: 
  `카메라 센서 점군(pts_cam) -> 좌표계 변환(T_base_cam) -> base 기준 점군 -> Lstsq 평면 잔차 이상치 제거 -> PCA/Kabsch 자세 추정(T_goal) -> SLERP(회전) + Cubic Spline(위치) 궤적 생성 -> 60프레임 애니메이션 시연`
- 모듈 ③ 에서 가져온 함수와 이번에 새로 만든 함수 구분:
  - **모듈 ③ 재사용:** `default_chain`, `rodrigues`, `rot_x`, `rot_y`, `rot_z`, `make_T`, `inv_T`, `transform_points`, `matrix_to_quaternion`, `quaternion_to_matrix`, `slerp`, `cubic_spline_interp`, `linear_interp`, `finite_diff`
  - **이번 신규 구현 (`src/pose_estimation.py`):** `pca_axes`, `kabsch`, `fit_plane_lstsq`, `remove_outliers`, `rotation_angle_deg`

## 2. 자세 추정 결과와 오차

- PCA 주축 3개와 고유값:
  - 주축 1(X): `[0.999616, -0.027664, 0.001692]` ($\lambda_1 = 0.122479$)
  - 주축 2(Y): `[0.027668, 0.999615, -0.001853]` ($\lambda_2 = 0.009899$)
  - 주축 3(Z): `[-0.001639, 0.001899, 0.999997]` ($\lambda_3 = 0.002537$)
- Kabsch 로 추정한 회전과 참값 사이 각도 오차: `0.91` 도, 병진 오차: `0.006` m
- 이상치 제거 전후 오차: `12.45` 도 -> `0.93` 도 (이상치 12개 100% 제거)
- 정합 전후 그림 (03 노트북 캡처): `5-3 및 5-5 셀의 3D Plot Visualizations 참조 (정합 후 RMS가 노이즈 수준인 0.03m 이내로 수렴)`

## 3. 노이즈·점 개수가 정확도에 미친 영향

- 노이즈 0 ~ 0.25 스윕에서 오차가 어떻게 커졌는가: 
  노이즈 표준편차 $\sigma$에 비례하여 Kabsch 회전 추정 오차가 선형적으로(Linear) 가파르게 증가함.
- 점 개수 30 / 90 / 270 계열 비교 — 점이 많을수록 오차가 줄어드는 정도 (대략 몇 배):
  점 개수 $N$이 9배($30 \rightarrow 270$) 증가함에 따라 오차는 약 $\frac{1}{\sqrt{9}} = \frac{1}{3}$ 배 수준으로 감소함.
- 구형 점군에서 PCA 주축이 불안정해진 이유 (고유값 관점):
  세 축의 표준편차가 비슷하면 고유값 간격이 좁아져 고유값이 축퇴($\lambda_1 \approx \lambda_2$)됨. 이로 인해 대표 고유공간의 방향성 독점권이 상실되어 미세한 샘플링 오차만으로도 첫 주축이 $72.73^\circ$ 이상 무작위로 회전하게 됨.
- 오차 그래프 (03 노트북 캡처): `5-4 셀의 노이즈-점 개수별 각도 오차 곡선 그래프 참조`

## 4. 현재 구현의 한계

- 자세 추정: Kabsch 알고리즘은 기준 점군과 관측 점군 간의 1:1 포인트 대응(Correspondence)이 완벽히 알려진 경우에만 동작하며, 대칭적 물체에서는 PCA 주축의 부호 반전 모호성(Sign Ambiguity)이 발생함.
- 궤적 생성: 로봇의 관절 각도 한계(Joint Limit) 및 장애물 충돌 회피(Collision Avoidance)를 고려하지 않았으며, 최대 속도/가속도 물리적 임계값을 제한하는 프로파일이 미반영됨.
- 파이프라인: 카메라 - 그리퍼 간 센서 캘리브레이션 오차(Hand-Eye Calibration Error)가 완전히 미치지 않는 정밀 환경을 전제로 함.
- 시연: 단일 가상 강체만을 대상으로 수행되어 동적 환경이나 실제 그리퍼의 슬립(Slip) 현상을 반영하지 못함.

## 5. 개선한다면 무엇을 어떻게

- **대응이 없는 무작위 점군 정합:** ICP (Iterative Closest Point) 알고리즘 또는 FPFH 기반 3D Feature Matching 도입으로 점 대응 정보 없이도 정확한 자세 추정 수행.
- **고비율 이상치 환경 강건성 확보:** Lstsq 평면 피팅 대신 RANSAC (Random Sample Consensus) 알고리즘을 도입하여 이상치 비율이 50% 이상인 악조건에서도 정확한 법선 추정.
- **물리적 잔진동 최소화 궤적:** Minimum Jerk Trajectory(최소 저크 궤적) 기술을 도입하여 가속도의 변화율(Jerk)을 최적화하고 로봇 관절의 관속 무리를 최소화.
- 개선 효과를 어떻게 측정할 것인지: 
  - 정합 성공률(Success Rate) 및 ICP Convergence Iteration 수 측정
  - RANSAC 이상치 허용 한계 비율 테스트 (Outlier Breakdown Point 측정)
  - 궤적 가속도 점프 크기 및 로봇 관절 토크 RMS 수치 비교 측정

---

### 부록 — 재현 정보

- Python / 주요 패키지 버전 (`requirements.txt`): Python 3.10+, numpy, scipy, matplotlib, ipywidgets, pillow (최신 requirements.txt 반영 완료)
- 난수 시드: `np.random.default_rng(42)`
- 세 노트북 Restart Kernel and Run All 통과 여부: `PASS (모든 검증 셀 PASS 확인)`
- `demo.gif` 프레임 수: `60`