from collections import deque
import copy

def find_optimal_path(map_array, map_size):
    start = (map_size // 2, map_size // 2)
    dx = [1, -1, 0, 0]
    dy = [0, 0, 1, -1]
    three_pos = []

    for i in range(map_size):
        for j in range(map_size):
            if map_array[i][j] == 2:
                three_pos.append((i, j))

    three_index = {pos: idx for idx, pos in enumerate(three_pos)}
    total_three = len(three_pos)
    all_visited = (1 << total_three) - 1
    # visited[x][y][mask] ensures BFS doesn't revisit same state
    visited = [[[False] * (1 << total_three) for _ in range(map_size)] for _ in range(map_size)]
    parent = {}

    q = deque([(start[0], start[1], 0)])
    visited[start[0]][start[1]][0] = True
    end_state = None

    while q:
        x, y, bitmask = q.popleft()
        if bitmask == all_visited and map_array[x][y] == 0:
            end_state = (x, y, bitmask)
            break
        for d in range(4):
            nx, ny = x + dx[d], y + dy[d]
            if 0 <= nx < map_size and 0 <= ny < map_size:
                new_mask = bitmask
                if map_array[nx][ny] == 2:
                    idx = three_index[(nx, ny)]
                    new_mask |= (1 << idx)
                if not visited[nx][ny][new_mask]:
                    visited[nx][ny][new_mask] = True
                    parent[(nx, ny, new_mask)] = (x, y, bitmask)
                    q.append((nx, ny, new_mask))

    path_map = copy.deepcopy(map_array)
    if not end_state:
        print("경로를 찾을 수 없습니다.")
        return path_map

    # 역추적
    x, y, mask = end_state
    path_coords = []
    while (x, y, mask) in parent:
        path_coords.append((x, y))
        x, y, mask = parent[(x, y, mask)]
    path_coords.append((x, y))
    path_coords.reverse()

    # 중복 좌표 제거: 지나간 곳을 다시 지나가지 않도록
    unique_coords = []
    seen = set()
    for coord in path_coords:
        if coord not in seen:
            unique_coords.append(coord)
            seen.add(coord)
    path_coords = unique_coords

    # 번호 매기기 (0은 목적지)
    num = 4
    for x, y in path_coords:
        if map_array[x][y] != 0:
            path_map[x][y] = num
            num += 1

    print("최적 경로:")
    for row in path_map:
        print(row)
    return path_map

# 테스트
if __name__ == "__main__":
    map_data = [
        [1,1,2,1,1,2,1],
        [2,1,1,1,1,1,1],
        [1,1,1,1,1,1,1],
        [1,2,1,0,1,1,1],
        [1,1,1,1,1,2,1],
        [1,2,1,1,1,1,1],
        [1,1,1,1,2,1,1],
    ]
    find_optimal_path(map_data, 7)
