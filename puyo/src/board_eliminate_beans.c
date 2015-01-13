
#include <stdlib.h>
#include <stdbool.h>

#define MIN(a, b) ( (a)<(b) ? (a) : (b) )

static const int group_bonus_table[] = {0, 0, 0, 0, 0, 2, 3, 4, 5, 6, 7, 10};
static const int group_bonus_table_len = sizeof(group_bonus_table) / sizeof(group_bonus_table[0]);


void board_eliminate_beans(char* board, const int strides[2],
                           unsigned int* n_beans_out,
                           unsigned int* n_colors_out,
                           unsigned int* group_bonus_out);
static int get_color_idx(char color);
static bool should_eliminate(const char* board, const int strides[2],
                             bool visited[6][12],
                             int x, int y);
static int eliminate(char* board, const int strides[2],
                     char color, int x, int y);


/**
 * C implementation of `Board._eliminate_beans()`.
 */
void board_eliminate_beans(char* board, const int strides[2],
                           unsigned int* n_beans_out,
                           unsigned int* n_colors_out,
                           unsigned int* group_bonus_out) {
    unsigned int n_beans = 0;
    unsigned int group_bonus = 0;
    bool colors_eliminated[5] = {false, false, false, false, false};
    int n_colors = 0;
    bool visited[6][12];

    for(int x=0; x<6; x++) {
        for(int y=0; y<12; y++) {
            visited[x][y] = false;
        }
    }

    for(int x=0; x<6; x++) {
        for(int y=0; y<12; y++) {

            if(should_eliminate(board, strides, visited, x, y)) {
                char color = board[x*strides[0] + y*strides[1]];
                int n = eliminate(board, strides, color, x, y);
                n_beans += n;
                group_bonus += group_bonus_table[MIN(n, group_bonus_table_len-1)];

                int color_idx = get_color_idx(color);
                if(!colors_eliminated[color_idx]) {
                    n_colors++;
                }
                colors_eliminated[color_idx] = true;
            }

        }
    }

    *n_beans_out = n_beans;
    *n_colors_out = n_colors;
    *group_bonus_out = group_bonus;
}

static int get_color_idx(char color) {
    switch(color) {
        case 'r': return 0;
        case 'g': return 1;
        case 'b': return 2;
        case 'y': return 3;
        case 'p': return 4;
        case 'k': return 5;
        case ' ': return 6;
        default: return 7;
    }
}

static bool should_eliminate(const char* board, const int strides[2],
                             bool visited[6][12],
                             int x, int y) {
    int n_found = 1;
    char color = board[x*strides[0] + y*strides[1]];
    if(get_color_idx(color) >= 5 || visited[x][y]) {
        return 0;
    }

    // Stack of coordinates to check.
    // Start with just (x, y) in it.
    // The stack never needs to grow larger than 3, because we only push after
    // we find a matching color, and we quit when we find 4 matching.
    struct {int x; int y;} stack[3];
    int stack_n = 1;  // Number of items in the stack
    stack[0].x = x;
    stack[0].y = y;
    visited[x][y] = true;

    while(stack_n > 0) {

        // Pop (x, y)
        x = stack[stack_n-1].x;
        y = stack[stack_n-1].y;
        stack_n--;

        // Visit adjacent cells
        for(int dx=-1; dx<=1; dx++) {
            for(int dy=-1; dy<=1; dy++) {
                if(abs(dx+dy) != 1 || x+dx<0 || x+dx>=6 ||
                                      y+dy<0 || y+dy>=12) {
                    continue;
                }

                // If this adjacent cell is the same color
                if(!visited[x+dx][y+dy] &&
                   board[(x+dx)*strides[0] + (y+dy)*strides[1]] == color)
                {
                    visited[x+dx][y+dy] = true;
                    n_found++;
                    if(n_found >= 4) {
                        return true;
                    }

                    // Push (x+dy, y+dy)
                    stack[stack_n].x = x+dx;
                    stack[stack_n].y = y+dy;
                    stack_n++;

                }

            }
        }

    }

    return false;
}

static int eliminate(char* board, const int strides[2],
                     char color, int x, int y) {
    int n_eliminated = 1;
    board[x*strides[0] + y*strides[1]] = ' ';

    // Visit adjacent cells
    for(int dx=-1; dx<=1; dx++) {
        for(int dy=-1; dy<=1; dy++) {
            if(abs(dx+dy) != 1 || x+dx<0 || x+dx>=6 ||
                                  y+dy<0 || y+dy>=12) {
                continue;
            }
            int cell_idx = (x+dx)*strides[0] + (y+dy)*strides[1];

            if(board[cell_idx] == color) {
                n_eliminated += eliminate(board, strides, color, x+dx, y+dy);
            } else if(board[cell_idx] == 'k') {
                board[cell_idx] = ' ';
            }

        }
    }

    return n_eliminated;
}
