import github_data
import org_aggregation
import market_data
from loguru import logger
from library import log, env
from library.ghw import GithubWrapper


def main(include_crawl_github, include_org_data_update):
    log.configure()

    # NOTE: csv location can be local file or google spreadsheet, for example:
    #       https://docs.google.com/spreadsheets/d/<your_doc_id>/export?gid=0&format=csv
    csv_location = env.get("CSV_LOCATION")
    token = env.get("GITHUB_ACCESS_TOKEN")
    output_csv_filename = "api_data/github_data.csv"
    output_json_filename = "api_data/github_data.json"
    throttle_secs = float(env.get("THROTTLE_SECS"))

    logger.info(f"csv_location = {csv_location}")
    logger.info(f"output_csv_filename = {output_csv_filename}")
    logger.info(f"output_json_filename = {output_json_filename}")
    logger.info(f"throttle_secs = {throttle_secs}")

    ghw = GithubWrapper(token, throttle_secs)

    if include_crawl_github:
        # Crawl and write Github readme.md files & repo level API data csv/json
        github_data.process(csv_location, ghw, output_csv_filename, output_json_filename, throttle_secs)

    if include_org_data_update:
        # Aggregate repo level data by organisation
        in_repo_filename = "api_data/github_data.pkl"
        in_ticker_filename = "api_data/ticker_lookup.csv"
        output_org_csv_filename = "api_data/github_data_org.csv"
        output_org_json_filename = "api_data/github_data_org.json"
        org_aggregation.write_agg_data(in_repo_filename, in_ticker_filename, output_org_csv_filename, output_org_json_filename)


def test_coingecko():
    # TODO: WIP: Market data
    # market_data.test_coingeko()

    # TEMP: relevant_ticker_ids from CMC lookup matching by symbol in JupyterLab
    relevant_coin_ids = ['aave','cardano','binance-peg-cardano','singularitynet','algorand','alpha-finance','polyalpha-finance','amp-token','ankr','arweave','ark','cosmos','bakerytoken','band-protocol','bitcoin-diamond','bancor','bitcoin-cash-sv','bitcoin','bitcoin-gold','bittorrent-2','pancakeswap-token','celsius-degree-token','celo','celer-network','conflux-token','swissborg','nervos-network','compound-coin','compound-governance-token','coti','curve-dao-token','casper-network','cartesi','constellation-labs','dash','decred','dero','digibyte','dogecoin','binance-peg-dogecoin','binance-peg-polkadot','polkadot','dydx','elrond-erd-2','aelf','enjincoin','binance-peg-eos','eos','ethereum-classic','ethereum','energy-web-token','fei-protocol','fetch-ai','flow','fitmin','fantom','golem','gnosis','golden-ratio-token','the-graph','gatechain-token','hedera-hashgraph','hive','hymnode','helium','holotoken','hotnow','hydro-protocol','internet-computer','icon','impermax','injective-protocol','iotex','binance-peg-iotex','kava','klay-token','kusama','chainlink','livepeer','loopring','lisk','litecoin','binance-peg-litecoin','maidsafecoin','decentraland','matic-network','medibloc','minieverdoge','mina-protocol','iota','maker','melon','nano','near','neo','nexo','nkn','numeraire','nucypher','ocean-protocol','origin-protocol','omisego','menlo-one','harmony','one','one-hundred-coin-2','binance-peg-ontology','ontology','orbs','orchid-protocol','pha','polymath','quant-network','qtum','raiden-network','reef-finance','augur','request-network','revelation-coin','revain','rchain','iexec-rlc','oasis-network','rocket-pool','reserve-rights-token','thorchain-erc20','rune','thorchain','ravencoin','skale','status','havven','solana','serum','steem','storm','storj','stratis','blockstack','stox','sushi','syscoin','telcoin','tomochain','tron-bsc','tron','true-usd','uma','universe-token','uniswap','unicorn-token','vethor-token','waves','wax','chia','xdce-crowd-sale','ecash','nem','stellar','monero','ripple','binance-peg-xrp','verge','xyo-network','zcash','zencash','zilliqa','0x']
    # market_data.crawl_coins_by_ids(relevant_coin_ids)

    # market_cap, market_cap_rank, crawl_datetime= market_data.get_marketcap_by_cg_id("ethereum")
    # print(market_cap)

    # best_coin, coins = market_data.get_coins_by_symbol("eth")
    # print(best_coin)
    # result = market_data.get_coins_by_symbol("ada")
    # print(result[0])

    symbols = ['aave','ada','ada','agix','algo','alpha','alpha','amp','ankr','ar','ark','atom','bake','band','bcd','bnt','bsv','btc','btg','btt','cake','cel','celo','celr','cfx','chsb','ckb','comp','comp','coti','crv','cspr','ctsi','dag','dash','dcr','dero','dgb','doge','doge','dot','dot','dydx','egld','elf','enj','eos','eos','etc','eth','ewt','fei','fet','flow','ftm','ftm','glm','gno','grt','grt','gt','hbar','hive','hnt','hnt','hot','hot','hot','icp','icx','imx','inj','iotx','iotx','kava','klay','ksm','link','lpt','lrc','lsk','ltc','ltc','maid','mana','matic','med','med','mina','miota','mkr','mln','nano','near','neo','nexo','nkn','nmr','nu','ocean','ogn','omg','one','one','one','one','ont','ont','orbs','oxt','pha','poly','qnt','qtum','rdn','reef','rep','req','rev','rev','rev','rlc','rose','rpl','rsr','rune','rune','rune','rvn','skl','snt','snx','sol','srm','steem','stmx','storj','strax','stx','stx','sushi','sys','tel','tomo','trx','trx','tusd','uma','uni','uni','uni','vtho','waves','waxp','xch','xdc','xec','xem','xlm','xmr','xrp','xrp','xvg','xyo','zec','zen','zil','zrx']
    # coins_by_symbols = market_data.get_coins_by_symbols(symbols)
    # print(coins_by_symbols)

    # market_data.get_global()

    market_data.get_prices(relevant_coin_ids)


if __name__ == "__main__":
    # main(include_crawl_github=True, include_org_data_update=True)
    main(include_crawl_github=False, include_org_data_update=True)
    # test_coingecko()
