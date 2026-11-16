-- Dados de exemplo (usuários: flask --app run popular)

INSERT INTO servico (nome, preco, duracao_min) VALUES
  ('Corte', 40.00, 30),
  ('Barba', 30.00, 30),
  ('Corte e barba', 65.00, 60),
  ('Sobrancelha', 15.00, 15),
  ('Pigmentação', 50.00, 45);

INSERT INTO profissional (nome, telefone, hora_inicio, hora_fim) VALUES
  ('André', '(81) 99999-0001', '09:00', '18:00'),
  ('Bruno', '(81) 99999-0002', '09:00', '18:00'),
  ('Caio',  '(81) 99999-0003', '13:00', '20:00');

INSERT INTO cliente (nome, telefone) VALUES
  ('Lucas Almeida', '(81) 98888-0001'),
  ('Pedro Henrique', '(81) 98888-0002'),
  ('Mateus Silva', '(81) 98888-0003'),
  ('Rafael Costa', '(81) 98888-0004'),
  ('João Victor', '(81) 98888-0005'),
  ('Gabriel Souza', '(81) 98888-0006');
