from utils import tools

comment = " deposits eat slyly ironic, even instructions. \
express foxes detect slyly. blithely even accounts abov"
print(comment)

k = tools.prf_256(b"00111", "ridddd")
ct = tools.aes_enc(k, comment)
print(ct)
