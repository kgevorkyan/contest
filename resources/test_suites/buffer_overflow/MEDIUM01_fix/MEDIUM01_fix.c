/*
 * Based on CVE-2020-12654 (fixed)
 */

#include <string.h>

struct S {
  int a;
  char b;
};

struct P {
  unsigned short len;
  char *data;
};

int memcopy_r(char *dst, void *src, size_t sz) {
  if (sz > sizeof(struct S)) {
    return -1;
  }

  memcpy(dst, src, sz);
  return 0;
}

int main() {
  struct S str;
  struct P param;
  param.data = "34345438979797974945";
  param.len = strlen(param.data);
  memcopy_r((char *)&str, param.data, param.len);
}
