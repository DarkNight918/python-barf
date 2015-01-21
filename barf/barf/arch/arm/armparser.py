"""
ARM Instruction Parser.
"""

import copy
import logging
import os

from pyparsing import alphanums
from pyparsing import alphas
from pyparsing import Combine
from pyparsing import Forward
from pyparsing import Literal
from pyparsing import nums
from pyparsing import Optional
from pyparsing import Or
from pyparsing import Suppress
from pyparsing import Word
from pyparsing import ZeroOrMore
from pyparsing import Group
from pyparsing import LineEnd

from barf.arch import ARCH_ARM_MODE_32
from barf.arch.arm.armbase import ArmArchitectureInformation
from barf.arch.arm.armbase import ArmRegisterListOperand
from barf.arch.arm.armbase import ArmImmediateOperand
from barf.arch.arm.armbase import ArmInstruction
from barf.arch.arm.armbase import ArmMemoryOperand
from barf.arch.arm.armbase import ArmRegisterOperand
from barf.arch.arm.armbase import ArmShifterOperand
from barf.arch.arm.armbase import ARM_MEMORY_INDEX_OFFSET
from barf.arch.arm.armbase import ARM_MEMORY_INDEX_POST
from barf.arch.arm.armbase import ARM_MEMORY_INDEX_PRE

logger = logging.getLogger(__name__)

arch_info = None

# Parsing functions
# ============================================================================ #
def process_shifter_operand(tokens):
    
    base = process_register(tokens["base"])
    sh_type = tokens["type"]
    amount = tokens.get("amount", None)
    
    if amount:
        if "imm" in amount:
            amount = ArmImmediateOperand("".join(amount["imm"]))
        elif "reg" in amount:
            amount = process_register(amount["reg"])
        else:
            raise Exception("Unknown amount type.")
        
    return ArmShifterOperand(base, sh_type, amount)

def process_register(tokens):
    name = tokens["name"]
    # TODO: Add all reg sizes
#     size = arch_info.registers_size[name]
    size = 32
    oprnd = ArmRegisterOperand(name, size)
    
    return oprnd

def parse_operand(string, location, tokens):
    """Parse an ARM instruction operand.
    """

    if "immediate_operand" in tokens:
        oprnd = ArmImmediateOperand("".join(tokens["immediate_operand"]))

    if "register_operand" in tokens:
        oprnd =  process_register(tokens["register_operand"])

    if "memory_operand" in tokens:
        mem_oprnd = tokens["memory_operand"]

        if "offset" in mem_oprnd:
            index_type = ARM_MEMORY_INDEX_OFFSET
            mem_oprnd = mem_oprnd["offset"]
        elif "pre" in mem_oprnd:
            index_type = ARM_MEMORY_INDEX_PRE
            mem_oprnd = mem_oprnd["pre"]
        elif "post" in mem_oprnd:
            index_type = ARM_MEMORY_INDEX_POST
            mem_oprnd = mem_oprnd["post"]
        else:
            raise Exception("Unknown index type.")
            
        reg_base = process_register(mem_oprnd["base"])
        displacement = mem_oprnd.get("disp", None)
        disp_minus = True if mem_oprnd.get("minus") else False
        
        if displacement:
            if "shift" in displacement:
                displacement = process_shifter_operand(displacement["shift"])
            elif "reg" in displacement:
                displacement = process_register(displacement["reg"])
            elif "imm" in displacement:
                displacement = ArmImmediateOperand("".join(displacement["imm"]))
            else:
                raise Exception("Unknown displacement type.")

        oprnd = ArmMemoryOperand(reg_base, index_type, displacement, disp_minus)
        
    if "shifter_operand" in tokens:
        oprnd =  process_shifter_operand(tokens["shifter_operand"])
    
    if "register_list_operand" in tokens:
        parsed_reg_list = tokens["register_list_operand"]
        reg_list = []
        for reg_range in parsed_reg_list:
            start_reg = process_register(reg_range[0])
            if len(reg_range) > 1:
                end_reg = process_register(reg_range[1])
                reg_list.append([start_reg, end_reg])
            else:
                reg_list.append([start_reg])
            
        oprnd = ArmRegisterListOperand(reg_list)

    return oprnd

def parse_instruction(string, location, tokens):
    """Parse an ARM instruction.
    """
    prefix = tokens.get("prefix", None)
    mnemonic = tokens.get("mnemonic")
    operands = [op for op in tokens.get("operands", [])]

    instr = ArmInstruction(
        prefix,
        mnemonic,
        operands,
        arch_info.architecture_mode
    )

    return instr

# Grammar Rules
# ============================================================================ #
mul      = Literal("*")
plus     = Literal("+")
minus    = Literal("-")
comma    = Literal(",")
lbracket = Literal("[")
rbracket = Literal("]")
lbrace   = Literal("{")
rbrace   = Literal("}")
hashsign = Literal("#")
exclamation    = Literal("!")
caret   = Literal("^")

hex_num = Combine(Literal("0x") + Word("0123456789abcdef"))
dec_num = Word("0123456789")

# Operand Parsing
# ============================================================================ #
sign = Optional(Or([plus, minus("minus")]))

immediate = Group(Optional(Suppress(hashsign)) + (sign +  Or([hex_num, dec_num]))("value"))

register = Group(Or([
    Combine(Literal("r") + Word(nums)("reg_num")),
    Combine(Literal("d") + Word(nums)("reg_num")),
    Combine(Literal("c") + Word(nums)("reg_num")),
    Combine(Literal("p") + Word(nums)("reg_num")),
    Literal("sp"),
    Literal("lr"),
    Literal("pc"),
    Literal("fp"),
    Literal("ip"),
    Literal("sl"),
    Literal("sb"),
    Literal("cpsr"),
    Literal("fpscr"),
    Literal("apsr"),
    Literal("cpsr_fc"),
])("name") + Optional(exclamation))

shift_type = Or([
    Literal("lsl"),
    Literal("lsr"),
    Literal("asr"),
    Literal("ror"),
    Literal("rrx"),
])

shift_amount = Group(Or([immediate("imm"), register("reg")]))

shifter_operand = Group(register("base") + Suppress(comma) + shift_type("type") + Optional(shift_amount("amount")))

displacement = Group(Or([immediate("imm"), register("reg"), shifter_operand("shift")]))

offset_memory_operand = Group(
    Suppress(lbracket) + 
    register("base") +
    Optional(
        Suppress(comma) +
        sign +
        displacement("disp")
    ) +
    Suppress(rbracket)
)

pre_indexed_memory_operand = Group(
    Suppress(lbracket) + 
    register("base") +
    Suppress(comma) +
    sign +
    displacement("disp") +
    Suppress(rbracket) + 
    Suppress(exclamation)
)

post_indexed_memory_operand = Group(
    Suppress(lbracket) + 
    register("base") +
    Suppress(rbracket) +
    Suppress(comma) +
    sign +
    displacement("disp")
)

memory_operand = Group(Or([
    offset_memory_operand("offset"),
    pre_indexed_memory_operand("pre"),
    post_indexed_memory_operand("post")
]))

# TODO: Add ! to multiple load store
register_range = Group(register("start") + Optional(Suppress(minus) + register("end")))

register_list_operand = Group(
    Suppress(lbrace) +
    Optional(ZeroOrMore(register_range + Suppress(comma)) + register_range) +
    Suppress(rbrace)
)

operand = (Or([
    immediate("immediate_operand"),
    register("register_operand"),
    shifter_operand("shifter_operand"),
    memory_operand("memory_operand"),
    register_list_operand("register_list_operand")
])).setParseAction(parse_operand)

# Instruction Parsing
# ============================================================================ #
mnemonic = Word(alphanums)

instruction = (
    mnemonic("mnemonic") +
    Optional(ZeroOrMore(operand + Suppress(comma)) + operand)("operands") +
    LineEnd()
).setParseAction(parse_instruction)

class ArmParser(object):
    """ARM Instruction Parser.
    """

    def __init__(self, architecture_mode=ARCH_ARM_MODE_32):
        global arch_info, modifier_size

        arch_info = ArmArchitectureInformation(architecture_mode)

        self._cache = {}

    def parse(self, instr):
        """Parse an ARM instruction.
        """
        # Commented to get the exception trace of a parser error.
        try:
            instr_lower = instr.lower()
    
            if not instr_lower in self._cache:
                instr_asm = instruction.parseString(instr_lower)[0]
    
                self._cache[instr_lower] = instr_asm
    
            instr_asm = copy.deepcopy(self._cache[instr_lower])

            # self._check_instruction(instr_asm)
        except Exception as e:
            instr_asm = None
 
            error_msg = "Failed to parse instruction: %s"
 
            logger.error(error_msg, instr, exc_info=True)
             
            print("Failed to parse instruction: " + instr)
            print("Exception: " + str(e))

        return instr_asm

    def _check_instruction(self, instr):
        # Check operands size.
        assert all([oprnd.size in [8, 16, 32, 64, 80, 128]
                        for oprnd in instr.operands]), \
                "Invalid operand size: %s" % instr

        # Check memory operand parameters.
        assert all([oprnd.base or oprnd.index or oprnd.displacement
                        for oprnd in instr.operands
                            if isinstance(oprnd, ArmMemoryOperand)]), \
                "Invalid memory operand parameters: %s" % instr
