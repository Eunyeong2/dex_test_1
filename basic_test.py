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

    m.execute(pair_addr, msg, [("umlg", 1000)])
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
    
    before_lp_Amount = get_lp_token(my_addr)
    print("Lptoken amount (before withdraw) : {}".format(before_lp_Amount))

    bal = get_token_amount(pair_addr)
    nabal = get_native_token_amount(pair_addr)
    print("Before withdraw, PAIR's token amount:{}".format(bal))
    print("Before withdraw, PAIR's native token amount:{}".format(nabal))

    bal = get_token_amount(my_addr)
    nabal = get_native_token_amount(my_addr)
    print("Before withdraw, my token amount :{}".format(bal))
    print("Before withdraw, my native token amount :{}".format(nabal))

    #withdraw token liquidity
    remove = to_binary({"withdraw_liquidity": {}})
    msg = json.dumps(
        {"send": {"contract": pair_addr, "amount": "1000", "msg": remove}}).encode()
    m.execute(lp_addr, msg, [])

    after_lp_Amount = get_lp_token(my_addr)
    print("Lptoken amount (after withdraw) : {}".format(after_lp_Amount))
    
    bal = get_token_amount(pair_addr)
    nabal = get_native_token_amount(pair_addr)
    print("After withdraw, PAIR token's amount:{}".format(bal))
    print("After withdraw, PAIR native token's amount:{}".format(nabal))

    #query token amount (after)
    bal = get_token_amount(my_addr)
    nabal = get_native_token_amount(my_addr)
    print("After withdraw, native token's amount in my_addr :{}".format(bal))
    print("After withdraw, token's amount in my_addr :{}".format(nabal))


# withdraw native token
def testWithdrawLiquidity2():
    m.cheat_message_sender(my_addr)

    lp_Amount = get_lp_token(my_addr)
    print("lp_amount (before withdraw2) :{}".format(lp_Amount))

    bal = get_token_amount(pair_addr)
    nabal = get_native_token_amount(pair_addr)
    print("Before withdraw, PAIR's token amount:{}".format(bal))
    print("Before withdraw, PAIR's native token amount:{}".format(nabal))

    bal = get_token_amount(my_addr)
    nabal = get_native_token_amount(my_addr)    
    print("Before withdraw, my token amount:{}".format(bal))
    print("Before withdraw, my native token amount:{}".format(nabal))

    #withdraw_liquidity (token)
    # msg = json.dumps({"withdraw_liquidity": {"sender": lp_addr, "amount": 1000}}).encode()
    # m.execute(pair_addr, msg, [("umlg", 1000)])
    remove = to_binary({"withdraw_liquidity": {}})
    #msg = json.dumps({"send": {"contract": pair_addr, "amount": "1000", "msg": remove}}).encode()
    msg = json.dumps({"send": {"contract": pair_addr, "msg" : remove, "amount": "1000"}}).encode()

    m.execute(lp_addr, msg, [("umlg", 0)])
    
    lp_Amount = get_lp_token(my_addr)
    print("lp_amount (after withdraw2) :{}".format(lp_Amount))

    bal = get_token_amount(pair_addr)
    nabal = get_native_token_amount(pair_addr)
    print("After withdraw, PAIR's token amount:{}".format(bal))
    print("After withdraw, PAIR's native token amount:{}".format(nabal))

    bal = get_token_amount(my_addr)
    nabal = get_native_token_amount(my_addr)
    print("After withdraw, my token amount:{}".format(bal))
    print("After withdraw, my native token amount:{}".format(nabal))

#liquidity + swap test
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
        json.loads(decode_vec(m.wasm_query(token_addr, balance_query_msg2)))["balance"]
    )

    for i in range(1):
        bal = get_token_amount(my_addr)
        nabal = get_native_token_amount(my_addr)
        # similar to [ask_amount = (ask_pool - cp / (offer_pool + offer_amount)) * (1 - commission_rate)]
        #res = m.execute(pair_addr, native_to_token, [("umlg", 3000)])
        res = m.execute(token_addr, token_to_native, [])
        print(res.get_log())

    bal2 = int(
        json.loads(decode_vec(m.wasm_query(token_addr, balance_query_msg)))["balance"]
    )

    bal2_token = int(
        json.loads(decode_vec(m.wasm_query(token_addr, balance_query_msg2)))["balance"]
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

    balance_query_msg = json.dumps({"balance": {"address": my_addr}}).encode()
    bal1 = int(json.loads(decode_vec(m.wasm_query(token_addr, balance_query_msg)))["balance"])
    print("(Before swap) my token amount: {}".format(bal1))

    msg = json.dumps({"balance": {"address": my_addr,"denom": "umlg",}}).encode()
    bal_umlg = bytearray(m.bank_query(msg)).decode()
    print("(Before swap) my native token amount: {}".format(bal_umlg))

    balance_query_msg = json.dumps({"balance": {"address": pair_addr}}).encode()
    bal1 = int(json.loads(decode_vec(m.wasm_query(token_addr, balance_query_msg)))["balance"])
    print("(Before swap) PAIR's token amount: {}".format(bal1))

    msg = json.dumps({"balance": {"address": pair_addr,"denom": "umlg",}}).encode()
    bal_umlg = bytearray(m.bank_query(msg)).decode()
    print("(Before swap) PAIR's native token amount: {}".format(bal_umlg))

    #swap token to native token
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

    # similar to [ask_amount = (ask_pool - cp / (offer_pool + offer_amount)) * (1 - commission_rate)]
    m.execute(token_addr, token_to_native, [])

    balance_query_msg = json.dumps({"balance": {"address": my_addr}}).encode()
    bal1 = int(json.loads(decode_vec(m.wasm_query(token_addr, balance_query_msg)))["balance"])
    print("(After swap) my token amount: {}".format(bal1))

    msg = json.dumps({"balance": {"address": my_addr,"denom": "umlg",}}).encode()
    bal_umlg = bytearray(m.bank_query(msg)).decode()
    print("(After swap) my native token amount: {}".format(bal_umlg))

    balance_query_msg = json.dumps({"balance": {"address": pair_addr}}).encode()
    bal1 = int(json.loads(decode_vec(m.wasm_query(token_addr, balance_query_msg)))["balance"])
    print("(After swap) PAIR's token amount: {}".format(bal1))

    msg = json.dumps({"balance": {"address": pair_addr,"denom": "umlg",}}).encode()
    bal_umlg = bytearray(m.bank_query(msg)).decode()
    print("(After swap) PAIR's native token amount: {}".format(bal_umlg))

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

    # similar to [ask_amount = (ask_pool - cp / (offer_pool + offer_amount)) * (1 - commission_rate)]
    m.execute(pair_addr, native_to_token,[("umlg", 3000)])

    balance_query_msg = json.dumps({"balance": {"address": my_addr}}).encode()
    bal1 = int(json.loads(decode_vec(m.wasm_query(token_addr, balance_query_msg)))["balance"])
    print("(After two swap) my token amount: {}".format(bal1))

    msg = json.dumps({"balance": {"address": my_addr,"denom": "umlg",}}).encode()
    bal_umlg = bytearray(m.bank_query(msg)).decode()
    print("(After two swap) my native token amount: {}".format(bal_umlg))

    balance_query_msg = json.dumps({"balance": {"address": pair_addr}}).encode()
    bal1 = int(json.loads(decode_vec(m.wasm_query(token_addr, balance_query_msg)))["balance"])
    print("(After two swap) PAIR's token amount: {}".format(bal1))

    msg = json.dumps({"balance": {"address": pair_addr,"denom": "umlg",}}).encode()
    bal_umlg = bytearray(m.bank_query(msg)).decode()
    print("(After two swap) PAIR's native token amount: {}".format(bal_umlg))

    

if __name__ == "__main__":
    testAddLiquidity1() ##Ok
    testWithdrawLiquidity1()
    #testAddLiquidity3()
    #testWithdrawLiquidity2()
    #testWithdrawLiquidity3()
    #testSwap1() ##Ok
