# regex2dfa
このリポジトリはQiita記事[正規表現から決定性有限オートマトンを生成する](https://qiita.com/MikaL_trivial/items/298d4c2bde68841d1ffb)のために作成されたものです．

ゆえにライブラリとして十分な機能を備えているわけではないのでご注意ください．

## 動作確認済み環境

- Python : 3.12.4
- Lark : 1.2.2

## 使用方法

```python
dfa = DFA(r"a(b + ac)*(c* + ab)")
```
のように正規表現を渡すことでその正規表現が表す集合の要素を受理する決定性有限オートマトンを初期化します．

```python
dfa.is_accepted("aacacbacbccc")
```
とすることで引数として与えられた文字列が受理されるかどうかを判定できます．

`regex2dfa.py`の`__main__`内に具体的な使用例を記載しています．