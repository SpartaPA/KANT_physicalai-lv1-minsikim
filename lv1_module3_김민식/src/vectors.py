"""문제 1 — 벡터 연산 모듈. (학생 작성용 템플릿)

내적 · 사이각 · 정규화 · 정사영 · 반대칭행렬(외적) · 평면 법선과
가우스 소거 기반의 rank / 행렬식 / 역행렬을 **직접** 구현한다.

규칙
----
- `np.linalg` 는 노트북에서 **검산용으로만** 쓰고, 이 모듈 안에서는 쓰지 않는다.
  (`inverse_gauss_jordan` 이 던지는 `np.linalg.LinAlgError` 예외 타입만 예외)
- 각 함수의 docstring 에 적힌 계약(입력/출력/예외)을 그대로 지킨다.
  노트북의 검증 셀과 `tests/` 가 이 계약을 기준으로 채점된다.
- 구현을 마치면 `raise NotImplementedError(...)` 줄을 지운다.
"""

from __future__ import annotations

import numpy as np

__all__ = [
    "as_vector",
    "dot",
    "norm",
    "angle_between",
    "normalize",
    "project",
    "reject",
    "skew",
    "cross",
    "plane_normal",
    "row_echelon",
    "rank",
    "det",
    "gauss_eliminate",
    "inverse_gauss_jordan",
]


# ---------------------------------------------------------------- 기본 연산

def as_vector(v) -> np.ndarray:
    """입력(리스트/튜플/배열)을 1차원 float 배열로 변환한다.

    1차원이 아니면 ValueError 를 던진다.

    [구현 예시] 아래 세 줄이 이 파일에서 기대하는 코드 스타일이다.
    나머지 함수도 이런 식으로 채워 넣으면 된다.
    """
    arr = np.asarray(v, dtype=float)
    if arr.ndim != 1:
        raise ValueError(f"1차원 벡터가 필요합니다. 받은 shape={arr.shape}")
    return arr


def dot(a, b) -> float:
    """내적. sum(a_i * b_i) 를 직접 계산한다 (`np.dot` 사용 금지).

    두 벡터의 차원이 다르면 ValueError.
    """
    # TODO: 문제 1-1
    va = as_vector(a)
    vb = as_vector(b)
    if (len(va) != len(vb)):
        raise ValueError(f"두 array의 길이가 다릅니다. a:{len(va)}, b:{len(vb)}")
    # for x,y in zip(a, b):
    #     total += x*y
    i=0
    total = 0
    while(i<len(va)):
        total += va[i] * vb[i]
        i += 1
    return float(total)


def norm(v) -> float:
    """유클리드 노름. sqrt(v·v) — 위에서 만든 dot 을 재사용한다."""
    # TODO: 문제 1-1
    return np.sqrt(dot(v,v))


def angle_between(a, b, degrees: bool = True) -> float:
    """두 벡터 사이각. degrees=True 면 도(°), False 면 라디안.

    cos(theta) = (a·b) / (|a||b|)

    주의 1. 영벡터가 들어오면 사이각이 정의되지 않는다 -> ValueError.
    주의 2. 부동소수점 오차로 |cos| 가 1 을 아주 조금 넘으면 arccos 가 nan 을 낸다.
            [-1, 1] 로 clip 해야 무작위 입력에서도 안전하다.
    """
    # TODO: 문제 1-1
    an = norm(a)
    bn = norm(b)
    d = dot(a,b)
    # print(f"an:{an}, bn:{bn}")
    if (np.isclose(an,0) or np.isclose(bn,0)):
        raise ValueError("norm이 0입니다.")
    arc = np.arccos(np.clip(d/(an*bn), -1, 1))
    # print(f"arccos({ac})")
    # if (ac > 1 or ac < -1):
    #     raise ValueError(f"값이 1을 초과하거나 -1보다 작습니다. {ac}")
    if degrees:
        return np.rad2deg(arc)
    else:
        return arc


def normalize(v, eps: float = 1e-12) -> np.ndarray:
    """단위벡터로 정규화한다. v / |v|

    영벡터를 어떻게 처리할지는 **문제 1-2 에서 직접 정한다.**
    노트북 1-2 에서 (1) 아무 처리 없이 나눴을 때 무슨 일이 나는지 관찰하고,
    (2) 선택한 처리 방식과 근거를 마크다운에 적은 뒤, 그 방식대로 여기에 구현한다.
    선택에 따라 노트북/테스트의 검증 코드도 그 방식에 맞춰 작성한다.
    """
    # TODO: 문제 1-2
    norm_v = norm(v)
    if norm_v < eps:
        raise ValueError(f"0에 가까운 벡터는 정규화할 수 없습니다.")
    return v / norm_v


def project(a, b) -> np.ndarray:
    """a 를 b 방향으로 정사영한 성분.

        proj_b(a) = (a·b / b·b) * b

    분모가 |b|^2 이므로 b 를 미리 정규화할 필요는 없다.
    b 가 영벡터면 ValueError.
    """
    # TODO: 문제 1-3
    if (np.all(b == 0)):
        raise ValueError(f"b가 영벡터입니다.")
    return dot(a,b) / dot(b,b) * b


def reject(a, b) -> np.ndarray:
    """a 에서 b 방향 성분을 뺀 나머지(수직 성분). a = project + reject 가 성립해야 한다."""
    # TODO: 문제 1-3
    return a - project(a, b)


def skew(a) -> np.ndarray:
    """3차원 벡터 a 에 대응하는 반대칭행렬 [a]_x 를 만든다.

        [a]_x = [[  0, -a3,  a2],
                 [ a3,   0, -a1],
                 [-a2,  a1,   0]]

    만족해야 하는 성질: [a]_x @ b == a x b,  [a]_x.T == -[a]_x
    3차원이 아니면 ValueError.
    """
    # TODO: 문제 1-4
    if (len(a) != 3):
        raise ValueError(f"벡터가 3차원이 아닙니다. {a}")
    ax = a[0]
    ay = a[1]
    az = a[2]
    return np.array([[0, -az, ay], 
                     [az, 0, -ax], 
                     [-ay, ax, 0]])


def cross(a, b) -> np.ndarray:
    """외적을 **반대칭행렬 곱으로** 계산한다 (`np.cross` 사용 금지)."""
    # TODO: 문제 1-4
    return skew(a) @ b
    # return np.array([a[1]*b[2]-a[2]*b[1], 
    #                  -a[0]*b[2]+a[2]*b[0], 
    #                  a[0]*b[1]-a[1]*b[0]])


def plane_normal(P1, P2, P3) -> np.ndarray:
    """세 점이 이루는 평면의 **단위** 법선 벡터.

    두 모서리 벡터(P2-P1, P3-P1)의 외적이 평면에 수직이다.
    세 점이 일직선이면 외적이 영벡터가 되어 평면이 하나로 정해지지 않는다 -> ValueError.
    """
    # TODO: 문제 1-5
    p1 = as_vector(P1)
    p2 = as_vector(P2)
    p3 = as_vector(P3)
    v1 = p2 - p1
    v2 = p3 - p1
    cross_v = cross(v1, v2)
    norm_v = norm(cross_v)
    if norm_v == 0:
        raise ValueError(f"세 점이 일직선이어서 외적이 영벡터입니다.")
    
    return cross_v / norm_v
    


# ------------------------------------------------- 가우스 소거 기반 선형대수

def row_echelon(A, pivoting: bool = True):
    """행 사다리꼴(row echelon form) 로 만든다.

    Parameters
    ----------
    pivoting : True 면 부분 피벗팅(각 열에서 절댓값이 가장 큰 행을 피벗으로 올림)

    Returns
    -------
    U : (m, n) 상삼각 형태 행렬
    pivot_cols : 피벗이 선 열 인덱스 리스트
    n_swaps : 행 교환 횟수 (행렬식 부호 계산에 필요)

    힌트: 0 인지 판정할 때는 `== 0` 대신 허용오차(tol)를 쓴다.
          예) tol = max(m, n) * np.finfo(float).eps * max(1.0, np.max(np.abs(U)))
    """
    # TODO: 문제 1-6 / 문제 4
    U = np.array(A, dtype=float, copy=True)
    # m = m.astype(float).copy()
    
    rows, cols = U.shape
    pivot_row = 0
    n_swaps = 0
    pivot_cols = []
    
    for col in range(cols):
        column = U[pivot_row:, col]
        # 해당 열이 모두 0이면 여기선 피봇을 찾을수없음, 다음 열로 이동
        if np.all(np.isclose(column, 0)):
            continue
        
        if pivoting:
            pivot = pivot_row + np.argmax(np.abs(column))
        else:
            # 열에서 0이아닌 값 찾기
            pivot = pivot_row
            while pivot < rows and np.isclose(U[pivot, col], 0):
                pivot += 1
        
        # 0이 아닌 값을 찾으면 피봇으로 지정해서 위로 올림
        # 피봇_row와 피봇 두 행을 바꿈, [[]]와 [][]는 다름
        U[[pivot_row, pivot]] = U[[pivot, pivot_row]]
        if pivot_row != pivot:
            n_swaps += 1
        
        for r in range(pivot_row + 1, rows):
            factor = U[r, col] / U[pivot_row, col]
            U[r] = U[r] - factor * U[pivot_row]
        pivot_cols.append(pivot_row)
        pivot_row += 1
        
        if pivot_row == rows:
            break
        
    return U, pivot_cols, n_swaps


def rank(A) -> int:
    """행 사다리꼴의 피벗 개수 = rank."""
    # TODO: 문제 1-6
    U, pivot_cols, n_swaps = row_echelon(A)
    return len(pivot_cols)

def det(A) -> float:
    """행렬식 = 행 사다리꼴 대각성분의 곱 x (-1)^(행 교환 횟수).

    피벗이 n 개보다 적으면(특이행렬) 0.0 을 돌려준다.
    정사각 행렬이 아니면 ValueError.
    """
    # TODO: 문제 1-6
    U, pivot_cols, n_swaps = row_echelon(A)
    if U.shape[0] != U.shape[1]:
        raise ValueError(f"정사각 행렬이 아닙니다. {U.shape}")
    if len(pivot_cols) < U.shape[0]:
        return 0
    total = 1.0
    for i in range(U.shape[0]):
        total *= U[i][i]
    # total = np.prod(np.diag(U))
    if n_swaps % 2 == 1: # 행을 한번 바꿀때마다 부호도 바뀜
        total *= -1
    return total

def gauss_eliminate(A, b, pivoting: bool = True, verbose: bool = False):
    """가우스 소거법 + 후진대입으로 Ax = b 를 푼다.

    Parameters
    ----------
    pivoting : True 면 부분 피벗팅을 적용한다. False 면 피벗을 그대로 쓴다
               (문제 4-4 에서 두 경우의 오차를 비교하므로 **둘 다 동작해야 한다**).
    verbose  : True 면 각 소거 단계의 첨가행렬 [A|b] 를 출력한다
               (문제 4-1 이 요구하는 '단계별 출력').

    Returns
    -------
    x : 해 벡터
    steps : 단계별 첨가행렬 [A|b] 스냅샷 리스트 (초기 상태 포함)

    피벗이 0 이면 해가 유일하지 않다 -> ZeroDivisionError.
    """
    # TODO: 문제 4-1
    U = np.array(np.hstack(A, b), dtype=float, copy=True)
        # m = m.astype(float).copy()
    rows, cols = U.shape
    pivot_row = 0
    n_swaps = 0
    x = np.zeros(rows)
    steps = []
    
    for col in range(cols):
        column = U[pivot_row:, col]
        # 해당 열이 모두 0이면 여기선 피봇을 찾을수없음, 다음 열로 이동
        if np.all(np.isclose(column, 0)):
            continue
        
        if pivoting:
            pivot = pivot_row + np.argmax(np.abs(column))
        else:
            # 열에서 0이아닌 값 찾기
            pivot = pivot_row
            while pivot < rows and np.isclose(U[pivot, col], 0):
                pivot += 1
        
        # 0이 아닌 값을 찾으면 피봇으로 지정해서 위로 올림
        # 피봇_row와 피봇 두 행을 바꿈, [[]]와 [][]는 다름
        U[[pivot_row, pivot]] = U[[pivot, pivot_row]]
        n_swaps += 1
        if verbose:
            print(f"\n행 교환: R{pivot_row} <-> R{pivot}")
            print(U)
        
        for r in range(pivot_row + 1, rows):
            factor = U[r, col] / U[pivot_row, col]
            U[r] = U[r] - factor * U[pivot_row]
            print(f"소거: R{r} <- R{r} - {factor}R{pivot_row}")
            print(U)
        
        pivot_row += 1
        
        if pivot_row == rows:
            break
    
    for i in range(rows-1, -1, -1): # rows-1부터 0까지 i--
        x[i] = U[i, -1] # 1. 끝에서부터 b값 넣음, 예: [0 0 2 | 4] => x[-1] = 4
        for j in range(i+1, rows): # 처음엔 rows-1+1 == rows이므로 실행안됨
            x[i] -= U[i,j] * x[j] # b값에 x와 계수를 곱해 빼줌, 예: [0 3 1 | 5] -> 5-(3*0)-(1*2) = 3
        
        x[i] /= U[i, i] # 계수로 나눠줌, 예: [0 0 2 | 4], x[-1] = 4 / 2 = 2
    
    return x, steps
    


def inverse_gauss_jordan(A) -> np.ndarray:
    """가우스-조던 소거로 역행렬을 구한다. [A|I] -> [I|A^-1].

    정사각이 아니면 ValueError, 특이행렬이면 np.linalg.LinAlgError.
    (`np.linalg.inv` 를 부르지 말고 소거로 직접 구한다)
    """
    # TODO: 문제 4-3
    I = np.eye(3)
    U = np.array(np.hstack(A, I), dtype=float, copy=True)
    # m = m.astype(float).copy()
    rows, cols = U.shape
    pivot_row = 0
    n_swaps = 0
    x = np.zeros(rows)
    steps = []
    
    for col in range(cols):
        column = U[pivot_row:, col]
        # 해당 열이 모두 0이면 여기선 피봇을 찾을수없음, 다음 열로 이동
        if np.all(np.isclose(column, 0)):
            continue
        
        # pivoting
        pivot = pivot_row + np.argmax(np.abs(column))
        
        # 0이 아닌 값을 찾으면 피봇으로 지정해서 위로 올림
        # 피봇_row와 피봇 두 행을 바꿈, [[]]와 [][]는 다름
        U[[pivot_row, pivot]] = U[[pivot, pivot_row]]
        n_swaps += 1
        
        for r in range(pivot_row + 1, rows):
            factor = U[r, col] / U[pivot_row, col]
            U[r] = U[r] - factor * U[pivot_row]
            print(f"소거: R{r} <- R{r} - {factor}R{pivot_row}")
            print(U)
        
        pivot_row += 1
        
        if pivot_row == rows:
            break
    
    for i in range(rows-1, -1, -1): # rows-1부터 0까지 i--
        x[i] = U[i, -1] # 1. 끝에서부터 b값 넣음, 예: [0 0 2 | 4] => x[-1] = 4
        for j in range(i+1, rows): # 처음엔 rows-1+1 == rows이므로 실행안됨
            x[i] -= U[i,j] * x[j] # b값에 x와 계수를 곱해 빼줌, 예: [0 3 1 | 5] -> 5-(3*0)-(1*2) = 3
        
        x[i] /= U[i, i] # 계수로 나눠줌, 예: [0 0 2 | 4], x[-1] = 4 / 2 = 2
    
    A_inv = U[:, rows:]
    
    return A_inv
    
