import asyncio
import boto3
from sympy import content
from app.config import Config
from app.retry import with_retry

#It will return whether content is good or bad by using action 
def _apply_guardrail_sync(config:Config,text:str,source:str)->dict:
    client=boto3.client("bedrock-runtime",region_name=config.aws_region)
    #This function is used to apply AWS guardrail
    return client.apply_guardrail(
        guardrailIdentifier=config.bedrock_guardrail_id,
        guardrailVersion=config.bedrock_guradrail_version,
        source=source,
        content=[{"text":{"text":text}}]#This format aws expects
    )
    
    
async def validate_input(config:Config,text:str)->tuple[bool,str]:
    response=await with_retry(
        lambda:asyncio.to_thread(_apply_guardrail_sync,config,text,"INPUT"),
        max_retries=config.llm_max_retries,
        delay=config.llm_retry_delay
    )
    
    if response.get("action")=="GUARDRAIL_INTERVENED":
        return False,"Input blocked by safety guardrail"
    return True,""


async def validate_Output(config:Config,text:str)->tuple[bool,str]:
    response=await with_retry(
        lambda:asyncio.to_thread(_apply_guardrail_sync,config,text,"OUTPUT"),
        max_retries=config.llm_max_retries,
        delay=config.llm_retry_delay
    )
    
    if response.get("action")=="GUARDRAIL_INTERVENED":
        return False,"Output blocked by safety guardrail"
    return True,""
    
