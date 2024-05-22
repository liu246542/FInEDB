from utils.tools import prf_any, gen_key

if __name__ == '__main__':
    test_str = "this is content"
    sk = gen_key(128)
    print(sk)
    res = prf_any(sk, test_str, 10)
    print(len(res))
