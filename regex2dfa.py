from lark import Lark, Transformer
from lark.tree import Tree
from collections import deque


class PreProcess(Transformer):
    def LETTER(self, tok):
        return tok.value


class DFA():
    def __init__(self, regex):
        parser = Lark(
            open("./regex.lark"),
            parser="lalr",
            transformer=PreProcess()
        )
        tree = parser.parse(regex)
        tree = Tree("concat", [tree, Tree("singleton", ["#"])])
        self.__regex = regex
        self.__generate_dfa(tree)
        self.reset()

    def get_transitions(self):
        return self.__transitions

    def get_accepting_states(self):
        return self.__accepting_states

    def get_init_state(self):
        return self.__init_state

    def get_current_state(self):
        return self.__current_state

    def set_current_state(self, state):
        self.__current_state = state

    def get_state_after_transitions(self, string):
        current_state = self.__current_state
        for i in range(len(string)):
            if current_state != -1 and string[i] in self.__transitions[current_state]:
                current_state = self.__transitions[current_state][string[i]]
            else:
                current_state = -1
        return current_state

    def get_regex(self):
        return self.__regex

    def is_accepted(self, string):
        current_state = self.__init_state
        for i in range(len(string)):
            if current_state != -1 and string[i] in self.__transitions[current_state]:
                current_state = self.__transitions[current_state][string[i]]
            else:
                current_state = -1
        return current_state in self.__accepting_states

    def reset(self):
        self.__current_state = self.__init_state

    def transition(self, string):
        for i in range(len(string)):
            if self.__current_state != -1 and string[i] in self.__transitions[self.__current_state]:
                self.__current_state = self.__transitions[self.__current_state][string[i]]
            else:
                self.__current_state = -1
        return self.__current_state

    def __generate_dfa(self, tree):
        index2letter = []
        self.__indexing_leaves(tree, index2letter)

        followpos = [set() for _ in range(len(index2letter))]
        root_nfl = self.__calc_nullable_first_last_follow(tree, followpos)
        self.__make_transitions(root_nfl["first"], index2letter, followpos)


    def __indexing_leaves(self, tree, index2letter):
        if tree.data == "singleton":
            index2letter.append(tree.children[0])
            tree.children[0] = {"value": tree.children[0], "index": len(index2letter) - 1}
            return
        for t in tree.children:
            self.__indexing_leaves(t, index2letter)

    def __calc_nullable_first_last_follow(self, tree, followpos):
        if tree.data == "singleton":
            return {"nullable": False, "first": {tree.children[0]["index"]}, "last": {tree.children[0]["index"]}}
        elif tree.data == "union":
            nfl_left = self.__calc_nullable_first_last_follow(tree.children[0], followpos)
            nfl_right = self.__calc_nullable_first_last_follow(tree.children[1], followpos)
            return {"nullable": nfl_left["nullable"] or nfl_right["nullable"],
                    "first": nfl_left["first"] | nfl_right["first"],
                    "last": nfl_left["last"] | nfl_right["last"]}
        elif tree.data == "concat":
            nfl_left = self.__calc_nullable_first_last_follow(tree.children[0], followpos)
            nfl_right = self.__calc_nullable_first_last_follow(tree.children[1], followpos)
            for i in nfl_left["last"]:
                followpos[i] |= nfl_right["first"]
            return {"nullable": nfl_left["nullable"] and nfl_right["nullable"],
                    "first": nfl_left["first"] | nfl_right["first"] if nfl_left["nullable"] else nfl_left["first"],
                    "last": nfl_left["last"] | nfl_right["last"] if nfl_right["nullable"] else nfl_right["last"]}
        elif tree.data == "kleene":
            nfl = self.__calc_nullable_first_last_follow(tree.children[0], followpos)
            for i in nfl["last"]:
                followpos[i] |= nfl["first"]
            return {"nullable": True,
                    "first": nfl["first"],
                    "last": nfl["last"]}
        else: # tree.data == "empty"
            return {"nullable": False, "first": set(), "last": set()}
    
    def __encode_state(self, state):
        code = 0
        for i in state:
            code += 1 << i
        return code

    def __make_transitions(self, init_state, index2letter, followpos):
        self.__transitions = {}
        self.__accepting_states = set()
        self.__init_state = self.__encode_state(init_state)
        waiting = deque()
        waiting.append(init_state)

        while len(waiting) > 0:
            current_state = waiting.popleft()
            current_state_code = self.__encode_state(current_state)
            if current_state_code in self.__transitions:
                continue
            self.__transitions[current_state_code] = {}
            next_states = {}
            for i in current_state:
                input_letter = index2letter[i]
                if input_letter == "#":
                    self.__accepting_states.add(current_state_code)
                    continue
                if input_letter in next_states:
                    next_states[input_letter] |= followpos[i]
                else:
                    next_states[input_letter] = followpos[i].copy()
            for (input_letter, next_state) in next_states.items():
                next_state_code = self.__encode_state(next_state)
                self.__transitions[current_state_code][input_letter] = next_state_code
                if not next_state_code in self.__transitions:
                    waiting.append(next_state)


if __name__ == "__main__":
    dfa = DFA(r"a(b + ac)*(c* + ab)")
    print(dfa.get_transitions())
    print(dfa.get_init_state())
    print(dfa.get_accepting_states())
    print(dfa.is_accepted("aacacbacbccc"))