"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.pc = 0
        self.reg = [0] * 8
        self.reg[7] = 0xf4  # stack pointer
        self.running = 0
        self.equal = 0
        self.less = 0
        self.greater = 0
        self.branchtable = {}
        self.branchtable[0b10000010] = self.handle_LDI
        self.branchtable[0b01000111] = self.handle_PRN
        self.branchtable[0b00000001] = self.handle_HLT
        self.branchtable[0b10100010] = self.handle_MUL
        self.branchtable[0b10100000] = self.handle_ADD
        self.branchtable[0b10101000] = self.handle_AND
        self.branchtable[0b10100111] = self.handle_CMP
        self.branchtable[0b01010100] = self.handle_JMP
        self.branchtable[0b01010101] = self.handle_JEQ
        self.branchtable[0b01010110] = self.handle_JNE
        self.branchtable[0b01000101] = self.handle_PUSH
        self.branchtable[0b01000110] = self.handle_POP
        self.branchtable[0b01010000] = self.handle_CALL
        self.branchtable[0b00010001] = self.handle_RET

    def ram_read(self, address):
        if address >= 0 and address <= 255:
            return self.ram[address]
        else:
            return "Address isn't within memory limits"

    def ram_write(self, value, address):
        if address > 0 and address < 255:
            self.ram[address] = value
        else:
            return "Address isn't within memory limits"

    def handle_LDI(self, op_a, op_b):
        self.reg[op_a] = op_b

    def handle_PRN(self, op_a, op_b):
        print(self.reg[op_a])

    def handle_HLT(self, op_a, op_b):
        self.running = False

    def handle_MUL(self, op_a, op_b):
        self.alu("MULT", op_a, op_b)

    def handle_ADD(self, op_a, op_b):
        self.alu("ADD", op_a, op_b)

    def handle_AND(self, op_a, op_b):
        self.alu("AND", op_a, op_b)

    def handle_CMP(self, op_a, op_b):
        self.alu("CMP", op_a, op_b)

    def handle_JMP(self, op_a, op_b):
        jump_addr = self.ram[self.pc + 1]
        self.pc = self.reg[jump_addr]

    def handle_JEQ(self, op_a, op_b):
        if self.equal == 1:
            jump_addr = self.ram[self.pc + 1]
            self.pc = self.reg[jump_addr]
        else:
            self.pc += 2

    def handle_JNE(self, op_a, op_b):
        if self.equal == 0:
            jump_addr = self.ram[self.pc + 1]
            self.pc = self.reg[jump_addr]
        else:
            self.pc += 2

    def handle_PUSH(self, op_a, op_b):
        self.reg[7] -= 1
        value = self.reg[op_a]  # want to push

        # store on stack
        top_of_stack_addr = self.reg[7]
        self.ram[top_of_stack_addr] = value

    def handle_POP(self, op_a, op_b):
        top_of_stack_addr = self.reg[7]
        self.reg[op_a] = self.ram[top_of_stack_addr]

        self.reg[7] += 1

    def handle_CALL(self, op_a, op_b):
        # Push return address
        ret_addr = self.pc + 2
        self.reg[7] -= 1
        addr_to_push_to = self.reg[7]
        self.ram[addr_to_push_to] = ret_addr

        # Call the subroutine
        reg_num = self.ram[self.pc + 1]
        subroutine_addr = self.reg[reg_num]
        self.pc = subroutine_addr

    def handle_RET(self, op_a, op_b):
        # Pop return address off the stack
        top_of_stack = self.reg[7]
        ret_addr = self.ram[top_of_stack]
        self.reg[7] += 1

        self.pc = ret_addr

    def load(self):
        """Load a program into memory."""

        address = 0

        if len(sys.argv) != 2:
            print("Usage: ls8.py programName")
            sys.exit(1)

        doodlehop = sys.argv[1]
        try:
            with open(doodlehop) as f:
                for line in f:
                    line = line.strip()
                    temp = line.split()

                    if len(temp) == 0:
                        continue

                    if temp[0][0] == "#":
                        continue

                    try:
                        self.ram[address] = int(temp[0], 2)

                    except ValueError:
                        print(f"Invalid number: {temp[0]}")
                        sys.exit(1)
                    except IndexError:
                        print(f"Invalid index")
                        sys.exit(1)

                    address += 1

        except FileNotFoundError:
            print(f"Could not open {doodlehop}")
            sys.exit(1)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MULT":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "CMP":
            if self.reg[reg_a] == self.reg[reg_b]:
                self.equal = 1
                self.less = 0
                self.greater = 0
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.equal = 0
                self.less = 1
                self.greater = 0
            else:
                self.equal = 0
                self.less = 0
                self.greater = 1
        elif op == "AND":
            self.reg[reg_a] = self.reg[reg_a] & self.reg[reg_b]
        # elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        self.running = True

        while self.running:

            IR = self.ram_read(self.pc)
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)
            num_of_args = (IR >> 6) + 1

            try:
                self.branchtable[IR](operand_a, operand_b)
            except:
                print(f"Invalid instruction {IR} at address {self.pc}")
                sys.exit(1)

            if IR & 0b00010000 == 0:  # and self.jump == 1:  # If the pc was not set by the branchtable fn
                self.pc += num_of_args
