#include <stdlib.h>

struct char2 {
  char *a;
  char *b;
};

int main() {
  struct char2 *c2 = (struct char2 *)malloc(sizeof(struct char2));
  c2->a = (char *)malloc(sizeof(char)); // Memory allocation
  free(c2->a);                          // Free allocated memory for 'c2->a'
  free(c2);
  *(c2->a) = 'a'; // Use after free
  return 0;
}
