




"""
[MAIN PROGRAM LOOP]

if token['balance']:
    get pool reserves 
    check maximum input using get_tokens_in_for_ratio_out()
    check maximum output using get_tokens_out_from_tokens_in()
    call token_swap() using input and output amounts from the two functions 
    refresh balances and restart loop
"""


        # get quotes and execute SPELL -> sSPELL swaps only if we have a balance of SPELL

        if spell["balance"]:

            try:
                # token0 (x) is sSPELL
                # token1 (y) is SPELL
                x0, y0 = lp.getReserves.call()[0:2]
            except:
                # restarts loop if getReserves() fails
                continue 

            # find maximum SPELL input at desired sSPELL/SPELL ratio "C"
            if spell_in := get_tokens_in_for_ratio_out(
                pool_reserves_token0=x0,
                pool_reserves_token1=y0,
                # sSPELL (token0) out 
                token0_out=True,
                token0_per_token1=Decimal(
                    str(1 / (base_staking_rate * (1 + THRESHOLD_SPELL_TO_SSPELL)))
                ),
                fee=Decimal("0.003"),
            ):
                if spell_in > spell["balance"]:
                    spell_in = spell["balance"]

                # calculate sSPELL output from SPELL input calculated above (used by token_swap to get amountOutMin)
                sspell_out = get_tokens_out_for_tokens_in(
                    pool_reserves_token0=x0,
                    pool_reserves_token1=y0,
                    quantity_token1_in=spell_in,
                    fee=Decimal("0.003"),
                )

                print(
                    f"*** EXECUTING SWAP FOR {spell_in // (10 ** spell['decimals'])} SPELL ***"
                )
                if token_swap(
                    token_in_quantity=spell_in,
                    token_in_address=spell["address"],
                    token_out_quantity=sspell_out,
                    token_out_address=sspell["address"],
                    router=router,
                ):
                    balance_refresh = True 
                    if ONE_SHOT:
                        sys.exit("single shot complete!")