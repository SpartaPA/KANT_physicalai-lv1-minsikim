# 문제1. C++ 빌드 체계 세우기 — g++ 다중 파일 빌드와 CMake 전환
답안 템플릿
- 수동 2단계 빌드 명령 (터미널 입력)
- undefined reference 에러 메시지 (출력) — 컴파일 에러와의 차이 설명
컴파일 에러는 main.cpp -> main.o 컴파일 단계에서 에러가 나는것이고, 링크에러는 .o파일들의 링크단계에서 필요한 함수를 찾지못해 생기는 에러이다.
```
s$ g++ main.o -o motor
/usr/bin/ld: main.o: in function `main':
main.cpp:(.text+0x24): undefined reference to `Motor::Motor()'
/usr/bin/ld: main.cpp:(.text+0x3c): undefined reference to `Motor::SetSpeed(double)'
/usr/bin/ld: main.cpp:(.text+0x64): undefined reference to `Motor::GetSpeed()'
collect2: error: ld returned 1 exit status
```
- CMake 빌드 출력 (터미널 출력)
```
$ cd build
$ cmake ..
-- The C compiler identification is GNU 11.4.0
-- The CXX compiler identification is GNU 11.4.0
-- Detecting C compiler ABI info
-- Detecting C compiler ABI info - done
-- Check for working C compiler: /usr/bin/cc - skipped
-- Detecting C compile features
-- Detecting C compile features - done
-- Detecting CXX compiler ABI info
-- Detecting CXX compiler ABI info - done
-- Check for working CXX compiler: /usr/bin/c++ - skipped
-- Detecting CXX compile features
-- Detecting CXX compile features - done
-- Configuring done
-- Generating done
-- Build files have been written to: /home/pa18/git/KANT_physicalai-lv1-minsikim/lv1_module2_김민식/cpp_basics/build
```

```
$ make
[ 33%] Building CXX object CMakeFiles/motor_app.dir/main.cpp.o
[ 66%] Building CXX object CMakeFiles/motor_app.dir/motor.cpp.o
[100%] Linking CXX executable motor_app
[100%] Built target motor_app
```
- 증분 빌드 시 재컴파일된 파일: motor.cpp — 판단 근거
motor.cpp.o파일만 빌딩하는 로그 확인
```
$ make
Consolidate compiler generated dependencies of target motor_app
[ 33%] Building CXX object CMakeFiles/motor_app.dir/motor.cpp.o
[ 66%] Linking CXX executable motor_app
[100%] Built target motor_app
```

# 문제3. rclpy 노드 작성 — 거북이 상태 발행자와 구독자
## 답안 템플릿
- /turtle1/pose 필드 구성:
```
x: 5.544444561004639
y: 5.544444561004639
theta: 0.0
linear_velocity: 0.0
angular_velocity: 0.0
```
- ros2 topic hz /turtle_distance 출력: 평균 10.000 Hz
```
average rate: 9.998
min: 0.100s max: 0.100s std dev: 0.00016s window: 12
```
- 구독자 경고 로그 (터미널 출력)
```
[WARN] [1788706472.126889766] [distance_subscriber]: Distance warning: 7.841 m
```
1. 구독자 2개 동시 수신 확인 (양쪽 로그)
![alt text](image-1.png)
2. 정사각형 주행 캡처 (turtlesim 화면)
![alt text](image.png)
3. Ctrl+C 정상 종료 화면 (출력)
![alt text](image-2.png)
# 4. rclcpp 노드 작성 — C++ 발행자와 구독자
## 답안 템플릿
1. colcon build 성공 출력
![alt text](image-4.png)
2. rclpy 발행에서 rclcpp 구독으로 이어진 로그
![alt text](image-3.png)
3. rclpy와 rclcpp 대응 관계표 — 노드 생성 / 타이머 / 콜백 / 종료 (4행)

|기능|rclpy(Python)|rclcpp(C++)|
|---|---|---|
|노드 생성|rclpy.node에서 Node상속, super().__init__('name')|rclcpp::Node상속, 생성자 상속에 Node('name')|
|타이머|create_timer(주기,콜백)|create_wall_timer(주기, 콜백)|
|콜백|create_subscription(메세지타입,토픽,콜백,큐깊이)|create_subscription<메세지타입>(토픽,큐깊이,콜백)|
|종료|rclpy.shutdown()|rclcpp::shutdown()|

# 5. Service 와 Action — 즉시 응답과 장기 작업
답안 템플릿
- 호출한 내장 서비스와 타입 — 4행 표 (서비스 / 타입 / 요청 값 / 결과)
- Service 요청·응답 로그
- 데드락이 생기는 이유 — executor 관점 3줄 이내 서술
응답은 익스큐터를 통해 오기때문에 요청이 오면 익스큐터는 콜백을 기다리고 콜백은 응답을 기다리기 때문에 데드락이 생긴다.
- rotate_absolute 피드백 수신 로그 — remaining 이 줄어드는 흐름
- 취소 요청 처리 로그 — 취소 시점 각도: ___
- 통신 패턴 설계표 — 기능 / 선택한 모델 / 근거 (5행)
```
ros2 service list
/clear
/kill
/reset
/spawn
/turtle1/set_pen
/turtle1/teleport_absolute
/turtle1/teleport_relative
/turtlesim/describe_parameters
/turtlesim/get_parameter_types
/turtlesim/get_parameters
/turtlesim/list_parameters
/turtlesim/set_parameters
/turtlesim/set_parameters_atomically
```
```
$ ros2 service type /turtle1/teleport_absolute
turtlesim/srv/TeleportAbsolute
```
```
$ ros2 service type /turtle1/set_pen
turtlesim/srv/SetPen
```
```
$ ros2 service type /spawn
turtlesim/srv/Spawn
```
```
$ ros2 service type /clear
std_srvs/srv/Empty
```
*---로 요청(Request)과 응답(Response) 구분
```
$ ros2 interface show turtlesim/srv/TeleportAbsolute
float32 x
float32 y
float32 theta
---
```

```
$ ros2 interface show turtlesim/srv/SetPen
uint8 r
uint8 g
uint8 b
uint8 width
uint8 off
---
```

```
s$ ros2 interface show turtlesim/srv/Spawn
float32 x
float32 y
float32 theta
string name # Optional.  A unique name will be created and returned if this is empty
---
string name
```

```
$ ros2 interface show std_srvs/srv/Empty
---
```
