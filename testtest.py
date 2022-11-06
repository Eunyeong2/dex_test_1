from cwsimpy import Model
import requests
import yaml
import json
import base64


def to_binary(msg):
    return base64.b64encode(json.dumps(msg).encode()).decode("ascii")


def decode_vec(v):
    v = bytearray(v)
    return v.decode("utf-8")


my_addr = "wasm1w20htrmu36l2lvrxf2an54h2gwlwr3ydz50exd"
factory_id = 2385
token_id = 2386
pair_id = 2387
factory_addr = "wasm10sug9g8a72fpfh3hln8d652ft6s76sc4qfknyyn3nf8y3mrj2t5szhc5m7"
token_addr = "wasm1drfc9jnag5ut3aqayrvthd06m9rywh5zd5h29l968dexkdu6ltjsfsdlet"
lp_addr = "wasm1rs93c39qxrzvf380jlvzdws4aavfnwgrhcpwx2fapz33lcvfk7vqa8vp52"
pair_addr = "wasm1df068k5sndlw6kx02cg7sw4y40j3kme6ff39u6z8skgldzkjyufqmanckk"
RPC_URL = "https://rpc.malaga-420.cosmwasm.com:443"
RPC_BN = 2383460
m = Model(RPC_URL, RPC_BN, "wasm")


def get_lp_token(addr):
    query_msg = json.dumps({"balance": {"address": addr}}).encode()
    res = bytearray(m.wasm_query(lp_addr, query_msg)).decode("ascii")
    lp_Amount = json.loads(res)['balance']
    return int(lp_Amount)

def get_token_amount(addr):
    #token amount
    balance_query_msg = json.dumps({"balance": {"address": addr}}).encode()
    bal1 = int(json.loads(decode_vec(m.wasm_query(token_addr, balance_query_msg)))["balance"])
    return bal1

def get_native_token_amount(addr):
    msg = json.dumps({"balance": {"address": addr,"denom": "umlg",}}).encode()
    bal_umlg = bytearray(m.bank_query(msg)).decode()
    return bal_umlg

# AddLiquidity test by my token
def testAddLiquidity1():
    m.cheat_message_sender(my_addr)

    msg = json.dumps({"provide_liquidity": {
        "assets": [
            {
                "info": {"token": {"contract_addr": token_addr}},
                "amount": "1000"
            },
            {
                "info": {"native_token": {"denom": "umlg"}},
                "amount": "1000"
            }
        ],
        "slippage_tolerance": None,
        "receiver": None
    }}).encode()

    m.execute(pair_addr, to_binary(msg), [("umlg", 1000)])
    first_lp_Amount = get_lp_token(my_addr)

    msg2 = json.dumps({"provide_liquidity": {
        "assets": [
            {
                "info": {"token": {"contract_addr": token_addr}},
                "amount": "2000"
            },
            {
                "info": {"native_token": {"denom": "umlg"}},
                "amount": "2000"
            }
        ],
        "slippage_tolerance": None,
        "receiver": None
    }}).encode()

    m.execute(pair_addr, msg2, [("umlg", 2000)])
    second_lp_Amount = get_lp_token(my_addr) - first_lp_Amount
    assert second_lp_Amount == first_lp_Amount*2

    msg = json.dumps({"provide_liquidity": {
        "assets": [
            {
                "info": {"token": {"contract_addr": token_addr}},
                "amount": "1000"
            },
            {
                "info": {"native_token": {"denom": "umlg"}},
                "amount": "1000"
            }
        ],
        "slippage_tolerance": None,
        "receiver": None
    }}).encode()
    m.execute(pair_addr, msg, [("umlg", 1000)])
    third_lp_Amount = get_lp_token(my_addr) - first_lp_Amount - second_lp_Amount
    assert third_lp_Amount == first_lp_Amount

# # provide different token test
# def testAddLiquidity3():
#     ttoken = "wasmd1asdf"
#     m.cheat_message_sender(my_addr)

#     msg = json.dumps({"provide_liquidity": {
#         "assets": [
#             {
#                 "info": { "token": { "contract_addr": ttoken } },
#                 "amount": "100"
#             },
#             {
#                 "info": { "native_token": { "denom": "umlg" } },
#                 "amount": "100"
#             }
#         ],
#         "slippage_tolerance": None,
#         "receiver": None
#     }}).encode()
#     m.execute(pair_addr, msg, [("umlg", 100)])
#     print(m.get_log)
#     lp_Amount = get_lp_token(my_addr)
#     print("testAddLiquidity3: {}".format(lp_Amount))

# withdraw token


def testWithdrawLiquidity1():
    m.cheat_message_sender(my_addr)
    print("before token", get_token_amount(my_addr))
    print("before native token", get_native_token_amount(my_addr))
    # testAddLiquidity1()
    # msg = json.dumps({"withdraw_liquidity": })
    lp_Amount = get_lp_token(my_addr)
    print("before lp: {}".format(lp_Amount))
    remove = to_binary(json.dumps({"withdraw_liquidity": {}}))
    #msg = json.dumps({"send":{}}).encode()
    msg = json.dumps(
        {"send": {"contract": pair_addr, "amount": "1000", "msg": remove}}).encode()
    m.execute(lp_addr, msg, [("umlg", 1000)])
    lp_Amount = get_lp_token(my_addr)
    print("After lp: {}".format(lp_Amount))
    print("after token", get_token_amount(my_addr))
    print(" native token", get_native_token_amount(my_addr))
    assert lp_Amount == 3000


# def testWithdrawLiquidity2():
#     m.cheat_message_sender(my_addr)

#     balance_query_msg = json.dumps({"balance": {"address": my_addr}}).encode()
#     bal1 = int(
#         json.loads(decode_vec(m.wasm_query(token_addr, balance_query_msg)))["balance"]
#     )
#     print("Before withdraw, native token amount:{}".format(bal1))
#     lp_Amount = get_lp_token(my_addr)
#     print("Before withdraw, lp_token amount: {}".format(lp_Amount))

#     remove = {"withdraw_liquidity" : {}}
#     msg = json.dumps({"send": {"contract": pair_addr, "amount": "1000", "msg" : }}).encode()
#     m.execute(pair_addr, msg, [("umlg", 3000)])
#     lp_Amount = get_lp_token(my_addr)

#     # bal2 = int(
#     #     json.loads(decode_vec(m.wasm_query(token_addr, balance_query_msg)))["balance"]
#     # )
#     bal1 = int(
#         json.loads(decode_vec(m.wasm_query(token_addr, balance_query_msg)))["balance"]
#     )
#     print("testWithdrawLiquidity2 token:{}".format(lp_Amount))
#     print("After withdraw, native token's amount:{}".format(bal1))


def testWithdrawLiquidity3():
    m.cheat_message_sender(my_addr)
    native_to_token = json.dumps(
        {
            "swap": {
                "offer_asset": {
                    "info": {"native_token": {"denom": "umlg"}},
                    "amount": "3000",
                },
                "belief_price": None,
                "max_spread": None,
                "to": None,
            }
        }).encode()

    token_to_native = json.dumps(
        {
            "send": {
                "contract": pair_addr,
                "amount": "3000",
                "msg": to_binary(
                    {
                        "swap": {
                            "belief_price": None,
                            "max_spread": None,
                            "to": my_addr,
                        }
                    }
                ),
            }
        }
    ).encode()
    balance_query_msg = json.dumps({"balance": {"address": my_addr}}).encode()
    balance_query_msg2 = json.dumps(
        {"balance": {"address": pair_addr}}).encode()

    bal1 = int(
        json.loads(decode_vec(m.wasm_query(token_addr, balance_query_msg)))[
            "balance"]
    )

    msg1 = json.dumps(
        {
            "balance": {
                "address": pair_addr,
                "denom": "umlg",
            }
        }).encode()

    msg2 = json.dumps(
        {
            "balance": {
                "address": pair_addr,
                "denom": "umlg",
            }
        }).encode()

    bal_umlg2 = bytearray(m.bank_query(msg1)).decode()

    bal_token = int(
        json.loads(decode_vec(m.wasm_query(token_addr, balance_query_msg2)))[
            "balance"]
    )

    for i in range(1):
        # similar to [ask_amount = (ask_pool - cp / (offer_pool + offer_amount)) * (1 - commission_rate)]
        #res = m.execute(pair_addr, native_to_token, [("umlg", 3000)])
        res = m.execute(token_addr, token_to_native, [])
        print(res.get_log())

    bal2 = int(
        json.loads(decode_vec(m.wasm_query(token_addr, balance_query_msg)))[
            "balance"]
    )

    bal2_token = int(
        json.loads(decode_vec(m.wasm_query(token_addr, balance_query_msg2)))[
            "balance"]
    )

    bal_umlg = bytearray(m.bank_query(msg2)).decode()

    print("(pair_addr)before native token balance : {} \n".format(bal_umlg2))
    print("(pair_addr)after native token balance : {} \n".format(bal_umlg))

    print("(pair_addr)before token amount:{}".format(bal_token))
    print("(pair_addr)after token amount:{}".format(bal2_token))

    print("before token balance: {}\n".format(bal1))
    print("after token balance : {}\n".format(bal2))


def testSwap1():
    m = Model(RPC_URL, RPC_BN, "wasm")
    m.cheat_message_sender(my_addr)
    msg = json.dumps({"provide_liquidity": {
        "assets": [
            {
                "info": {"token": {"contract_addr": token_addr}},
                "amount": "3000"
            },
            {
                "info": {"native_token": {"denom": "umlg"}},
                "amount": "4000"
            }
        ],
        "slippage_tolerance": None,
        "receiver": None
    }}).encode()

    m.execute(pair_addr, msg, [("umlg", 4000)])

    msg2 = json.dumps({"provide_liquidity": {
        "assets": [
            {
                "info": {"token": {"contract_addr": token_addr}},
                "amount": "60000"
            },
            {
                "info": {"native_token": {"denom": "umlg"}},
                "amount": "80000"
            }
        ],
        "slippage_tolerance": None,
        "receiver": None
    }}).encode()

    m.execute(pair_addr, msg2, [("umlg", 80000)])

    token_to_native = json.dumps(
        {
            "send": {
                "contract": pair_addr,
                "amount": "300",
                "msg": to_binary(
                    {
                        "swap": {
                            "belief_price": None,
                            "max_spread": None,
                            "to": my_addr,
                        }
                    }
                ),
            }
        }
    ).encode()
    balance_query_msg = json.dumps({"balance": {"address": my_addr}}).encode()
    m.execute(token_addr, token_to_native, [])

    bal1 = int(
        json.loads(decode_vec(m.wasm_query(token_addr, balance_query_msg)))[
            "balance"]
    )

    poolAmountX = (60000 + 3000) * 1e6
    poolAmountY = (80000 + 4000) * 1e6

    expectedOutput = -(int(poolAmountX * poolAmountY) /
                       int(poolAmountX + 300*1e6)) + int(poolAmountY)
    expectedOutput = expectedOutput * 999 / 1000
    print(expectedOutput)


if __name__ == "__main__":
    testAddLiquidity1()
    #testWithdrawLiquidity1()
    # testAddLiquidity3()
    #testWithdrawLiquidity2()
    # testWithdrawLiquidity3()
    # testSwap1()